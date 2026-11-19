# Recuperación del transporte AirLift: comparación 3105 2.2 vs proyecto antiguo

## Evidencia comprobada

- El proyecto antiguo incluye `PatchTransaction.swift` con operaciones de aplicación, inspección de restauración, restauración y recibos.
- En la versión compilada 2.2, el listado de tipos Swift incluye `AirLiftTransport`, `AirLiftPairingController`, `AirLiftPatchTransaction`, `AirLiftFileReference` y `AirLiftConnectionCheckGate`.
- El ZIP del decompilador contiene **declaraciones y metadatos**, no los cuerpos originales de las funciones Swift. No es posible copiar directamente AirLift 2.2 al proyecto antiguo desde esos encabezados.
- El proyecto antiguo marca iOS 27.0.1 y posteriores como no verificados en `ExploitSupportPolicy.isSupported`. Cambiar esa comprobación no otorga permisos de escritura sobre contenedores de terceros.

## Herramienta de comparación

```bash
python tools/compare_airlift_surfaces.py /ruta/3105_2.2_Decompiler.com.zip ThreeOneOSFive
```

La herramienta extrae nombres de clases/estructuras nuevas y los compara con los archivos Swift antiguos; es un análisis de solo lectura.

## Orden técnico de reconstrucción

1. Conservar el lector `PatchPackageCodec.swift` y la máquina de estados de `PatchTransaction.swift` del código antiguo.
2. Diseñar una interfaz de acceso a archivos que valide existencia, permisos, hash y copia de seguridad antes de aplicar cambios.
3. Implementar y probar esa interfaz primero con archivos del sandbox propio o seleccionados y autorizados por el usuario.
4. Recuperar de manera separada la experiencia visual de AirLift (diagnósticos, estados y errores); no presentar como funcional el transporte privilegiado sin pruebas.
5. Compilar con Xcode/Codemagic y recoger logs de **cada** versión objetivo en dispositivo real.

## Estado para iOS 27

Las versiones 27.0.1, 27.1, 27.2, 27.2.1 y 27.3 son **objetivos**, no versiones certificadas. Los metadatos de la IPA 2.2 no prueban por sí solos que un mismo mecanismo de acceso funcione en todas.

## Seguridad

No se cambió la detección de versiones para ejecutar código de kernel en compilaciones no verificadas ni se intentó eludir los controles de aislamiento de iOS.

## Recuperación de la superficie Swift desde la IPA

Se volvió a analizar **el ejecutable Mach-O**, no solo el ZIP de los encabezados. En la IPA 2.1 beta6 aparecen **1.875 nombres de símbolos Swift que contienen AirLift**. Entre los métodos visibles están `AirLiftTransport.probe`, `read`, `write`, `installedApplications`, `listEntries` y `AirLiftPatchTransaction.apply`, `restore` y `resetToAppliedState`. La IPA 2.2 conserva referencias y textos AirLift pero **no expone nombres Swift mangled con ese mismo patrón** en su ejecutable; el resultado del extractor es 0. Esto no significa que AirLift no esté presente en 2.2, sino que los símbolos correspondientes no están disponibles con ese método.

Herramienta reproducible (solo lectura):

```bash
python tools/extract_airlift_symbols.py /ruta/3105-2.1-beta6.ipa --contains 'AirLiftTransportO5write'
python tools/extract_airlift_symbols.py /ruta/3105-2.1-beta6.ipa --compare /ruta/3105-2.2.ipa
```

**Límite:** los nombres permiten identificar la estructura y firmas de parte de la API, pero no recuperan los cuerpos originales de las funciones. No habilitan por sí solos el acceso a archivos en iOS 27.
