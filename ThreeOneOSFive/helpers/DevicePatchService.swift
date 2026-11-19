import Foundation

/// A read-only diagnostic. A readable file is not necessarily writable:
/// iOS sandbox permissions must still be verified by the actual transaction.
struct PatchTargetAccessCheck: Identifiable {
    enum Status: Equatable {
        case readable
        case missing
        case inaccessible
        case containerUnavailable
        case invalidPath

        var localizationKey: String {
            switch self {
            case .readable: return "patch.path_check.readable"
            case .missing: return "patch.path_check.missing"
            case .inaccessible: return "patch.path_check.inaccessible"
            case .containerUnavailable: return "patch.path_check.container_unavailable"
            case .invalidPath: return "patch.path_check.invalid"
            }
        }
    }

    let id: UUID
    let bundleID: String
    let relativePath: String
    let status: Status
}

enum DevicePatchService {
    /// Inspect package targets without modifying any app data.
    /// This deliberately does not claim that an AirLift or MHA write will work.
    static func inspectPaths(project: PatchProject) -> [PatchTargetAccessCheck] {
        let targets: [(UUID, String, String)] =
            project.rules.map { ($0.id, $0.bundleID, $0.relativePath) }
            + project.directories.map { ($0.id, $0.bundleID, $0.relativePath) }
        var roots: [String: URL] = [:]
        var unavailableBundleIDs = Set<String>()
        let fileManager = FileManager.default

        return targets.map { id, bundleID, relativePath in
            let status: PatchTargetAccessCheck.Status
            do {
                guard try PatchPathValidator.canonicalBundleIdentifier(bundleID) == bundleID,
                      try PatchPathValidator.canonicalRelativePath(relativePath) == relativePath else {
                    throw PatchPackageError.unsafeTargetPath
                }

                let root: URL?
                if let cached = roots[bundleID] {
                    root = cached
                } else if unavailableBundleIDs.contains(bundleID) {
                    root = nil
                } else if let path = ContainerStore.resolveAppContainerPath(bundleID: bundleID),
                          ContainerStore.isApplicationContainerPath(path) {
                    root = PatchPathValidator.canonicalFileURL(
                        URL(fileURLWithPath: path, isDirectory: true)
                    )
                    roots[bundleID] = root
                } else {
                    root = nil
                    unavailableBundleIDs.insert(bundleID)
                }

                if let root {
                    let target = try PatchPathValidator.resolveContainedTargetURL(
                        relativePath: relativePath,
                        containerRoot: root
                    )
                    if !fileManager.fileExists(atPath: target.path) {
                        status = .missing
                    } else if let values = try? target.resourceValues(forKeys: [.isSymbolicLinkKey]),
                              values.isSymbolicLink != true,
                              fileManager.isReadableFile(atPath: target.path) {
                        status = .readable
                    } else {
                        status = .inaccessible
                    }
                } else {
                    status = .containerUnavailable
                }
            } catch {
                status = .invalidPath
            }
            return PatchTargetAccessCheck(
                id: id, bundleID: bundleID, relativePath: relativePath, status: status
            )
        }
    }

    static func apply(project: PatchProject) throws -> PatchTransactionReceipt {
        let bundleIDs = orderedBundleIdentifiers(in: project)
        return try withResolvedContainers(bundleIDs: bundleIDs) { roots in
            try PatchTransaction.apply(
                project: project,
                backupRoot: try PatchProjectLibrary.backupRootURL(),
                containerResolver: { bundleID in
                    guard let root = roots[bundleID] else {
                        throw PatchPackageError.targetAppUnavailable(bundleID)
                    }
                    return root
                }
            )
        }
    }

    static func inspectRestore(receipt: PatchTransactionReceipt) throws -> PatchRestoreInspection {
        let bundleIDs = try PatchTransaction.requiredBundleIdentifiers(for: receipt)
        return try withResolvedContainers(bundleIDs: bundleIDs) { roots in
            try PatchTransaction.inspectRestore(
                receipt: receipt,
                containerResolver: { bundleID in
                    guard let root = roots[bundleID] else {
                        throw PatchPackageError.targetAppUnavailable(bundleID)
                    }
                    return root
                }
            )
        }
    }

    static func restore(
        receipt: PatchTransactionReceipt,
        allowChangedTargets: Bool = false
    ) throws {
        let bundleIDs = try PatchTransaction.requiredBundleIdentifiers(for: receipt)
        try withResolvedContainers(bundleIDs: bundleIDs) { roots in
            try PatchTransaction.restore(
                receipt: receipt,
                allowChangedTargets: allowChangedTargets,
                containerResolver: { bundleID in
                    guard let root = roots[bundleID] else {
                        throw PatchPackageError.targetAppUnavailable(bundleID)
                    }
                    return root
                }
            )
        }
    }

    static func resetToAppliedState(
        receipt: PatchTransactionReceipt,
        project: PatchProject
    ) throws {
        let bundleIDs = try PatchTransaction.requiredBundleIdentifiers(for: receipt)
        try withResolvedContainers(bundleIDs: bundleIDs) { roots in
            try PatchTransaction.resetToAppliedState(
                receipt: receipt,
                fallbackProject: project,
                containerResolver: { bundleID in
                    guard let root = roots[bundleID] else {
                        throw PatchPackageError.targetAppUnavailable(bundleID)
                    }
                    return root
                }
            )
        }
    }

    static func latestReceipt(projectID: UUID) -> PatchTransactionReceipt? {
        guard let backupRoot = try? PatchProjectLibrary.backupRootURL() else { return nil }
        return PatchTransaction.latestReceipt(projectID: projectID, backupRoot: backupRoot)
    }

    private static func orderedBundleIdentifiers(in project: PatchProject) -> [String] {
        project.allBundleIdentifiers
    }

    private static func withResolvedContainers<T>(
        bundleIDs: [String],
        operation: ([String: URL]) throws -> T
    ) throws -> T {
        var roots: [String: URL] = [:]

        for bundleID in bundleIDs {
            guard let path = ContainerStore.resolveAppContainerPath(bundleID: bundleID),
                  ContainerStore.isApplicationContainerPath(path) else {
                throw PatchPackageError.targetAppUnavailable(bundleID)
            }
            roots[bundleID] = PatchPathValidator.canonicalFileURL(URL(fileURLWithPath: path, isDirectory: true))
        }
        return try operation(roots)
    }
}
