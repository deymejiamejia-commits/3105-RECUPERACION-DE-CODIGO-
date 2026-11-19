# Recuperación de 3105 — estado comprobado

Este archivo conserva el proyecto Xcode antiguo proporcionado por el usuario. No es una restauración byte por byte de la IPA posterior.

## Confirmado

- El proyecto Xcode, pantallas SwiftUI, recursos y `PatchPackageCodec.swift` están presentes.
- Este código antiguo **no contiene** la pantalla de compra/activación de keys observada en la IPA más nueva.
- `PatchPackageCodec` admite paquetes con contenido AES-GCM y datos autenticados (AAD) por ID de paquete y versión.
- El paquete `AIM VIP ANTENA DRT PECHO(1).3105` pasó una comprobación de descifrado autenticado, con una regla de reemplazo para `com.dts.freefireth`.
- La política `ExploitSupportPolicy` antigua solo incluye ciertas betas iOS 27 y no enumera iOS 27.0.1.

## Comprobación sin escribir archivos

```
python -m pip install cryptography
python tools/inspect_3105.py '/ruta/a/paquete.3105'
```

El script solo muestra nombre, bundle IDs, rutas relativas y tamaños. No exporta el contenido del archivo de reemplazo ni aplica parches.

## Pendiente de pruebas

- Compilación en Xcode/macOS (no disponible en este entorno).
- Determinar cuáles funciones de la IPA más nueva no están en esta rama antigua.
- Validación en dispositivo real de las funciones de acceso a archivos permitidas por iOS.
- Compatibilidad con iOS 27.0.1: **no comprobada**. No se modifica la política para simular soporte no verificado.

## Seguridad

No se realizaron cambios al código de exploits, contenedores ni permisos del sistema. La modificación añadida es únicamente una utilidad de inspección fuera de la app.
