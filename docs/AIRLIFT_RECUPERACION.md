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
