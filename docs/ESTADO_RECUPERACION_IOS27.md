# Recuperación 3105 — evidencias y pruebas de iOS 27

Este documento acompaña el código fuente antiguo de `ThreeOneOSFive`. **No certifica** que la reconstrucción tenga las capacidades de la IPA 2.2.

## Insumos recibidos

- Proyecto Swift/Xcode antiguo y lector `.3105`, con transacciones y restauración.
- IPA posterior 2.2 y ZIP del decompilador.
- Paquete `.3105` de referencia con estructura autenticada v2.
- Dos videos mostrando el flujo de aplicación de paquetes en dispositivos reales.
- Repositorio de recuperación (este repositorio).

**No se necesitan más videos para iniciar la reconstrucción.**

## Evidencias recogidas

| Sistema | Evidencia de la app 3105 original | Estado de la reconstrucción |
| --- | --- | --- |
| iOS 27.0.1 | Solicitado por el propietario; sin prueba adjunta analizada | Sin comprobar |
| iOS 27.1 | Solicitado por el propietario; sin prueba adjunta analizada | Sin comprobar |
| iOS 27.2, build `24B119` | Video: paquete **Holo**; diálogo Apply Patch; termina como **Applied**; ofrece Reset to Package y Restore Originals. El propietario afirma que se observó el efecto en el juego. | Sin comprobar |
| iOS 27.2.1 | Solicitado por el propietario; sin prueba adjunta analizada | Sin comprobar |
| iOS 27.3 beta, build `24C5037i` | Video: paquete **Holograma Cuadros**; flujo Apply Patch; mensaje de operaciones completadas y estado Applied. | Sin comprobar |

**Alcance de esta evidencia:** los videos muestran las pantallas y mensajes que emitió la IPA original. La modificación efectiva de archivos externos se basa en la confirmación del propietario; no se inspeccionaron hashes ni logs del sistema durante esas pruebas. En ningún caso constituyen pruebas de la versión reconstruida.

## Lo que ya está en el código antiguo

1. `PatchPackageCodec.swift`: lectura/validación de paquetes y contenido autenticado.
2. `PatchTransaction.swift`: resolución de rutas, copia de seguridad, aplicación y restauración con recibos.
3. Pantallas SwiftUI del catálogo, paquetes, archivos y ajustes.
4. `ExploitSupportPolicy`: una lista de sistemas y builds reconocidos por el código antiguo.

La pantalla de keys de la IPA posterior no está en esta versión antigua; no se necesita introducir otro sistema de licencias para reconstruir su funcionalidad.

## Brecha técnica principal

La IPA 2.2 contiene nombres y metadatos de estructuras `AirLiftTransport`, `AirLiftPatchTransaction`, `AirLiftPairingController` y `AirLiftFileReference`. Los encabezados del decompilador **no incluyen implementaciones Swift completas** de esas funciones. La política de compatibilidad no aporta por sí sola autorización para acceder a contenedores de otras aplicaciones.

Por tanto:
- No marcar iOS 27.2 como soportado en `ExploitSupportPolicy` solamente porque el video de la IPA original funcione.
- No mostrar **Applied** en la reconstrucción si no hubo escritura verificable y copia de seguridad.
- Mantener separados el soporte de importación de paquetes y el acceso real a rutas de destino.

## Prueba de aceptación del código reconstruido

Cada versión y dispositivo debe pasar estas comprobaciones con archivos de prueba autorizados, antes de anunciar compatibilidad:

1. **Instalar y abrir:** compilación y firma, versión/build, arranque sin bloqueo por keys.
2. **Importar:** validar cabecera, metadatos, integridad AES-GCM/AAD, bundle ID y ruta relativa.
3. **Acceso:** demostrar lectura y escritura en un destino autorizado; si iOS lo niega, mostrar error explícito sin afirmar éxito.
4. **Aplicar:** copia de seguridad previa, escritura atómica, comparación SHA-256 del destino y recibo persistente.
5. **Reiniciar:** confirmar que el estado Applied se corresponde con el archivo y recibo.
6. **Restaurar:** recuperar los bytes originales, verificar SHA-256 y limpiar el estado aplicado.
7. **Errores:** rollback si falla una operación, ruta fuera del contenedor o archivo incompatible.

Para cada prueba se necesitan únicamente el resultado y **logs sin datos personales**, generados después de compilar la nueva versión. No hacen falta más videos de la IPA antigua.

## Próximo trabajo de implementación

- Auditar las llamadas existentes a `PatchTransaction.apply` y al resolvedor de contenedores.
- Separar los diagnósticos de lectura/escritura de la clasificación de versión de iOS.
- Conectar la interfaz de aplicación/restauración a resultados verificables, sin falsos positivos.
- Compilar con Xcode/Codemagic y ejecutar la matriz de pruebas en iPhone.

**Estado actual:** reconstrucción parcial. La compatibilidad real de AirLift con iOS 27.0.1/27.1/27.2/27.2.1/27.3 no está recuperada ni validada en el proyecto de este repositorio.
