<<<<<<< HEAD
# cod_autenticador

Componente independiente para validar el almacenamiento local de una extensión
de autenticación y generar códigos TOTP sin intervención manual.

## Estado actual

La primera versión implementa:

- descubrimiento seguro del perfil de Chrome en Windows;
- inspección de inventario del directorio LevelDB, en modo solo lectura;
- extracción únicamente heurística de texto visible para diagnóstico;
- generación TOTP con SHA-1, SHA-256 y SHA-512;
- una API estable para que una automatización futura solicite un código.

La inspección no modifica el perfil, no elimina `LOCK` y no considera que una
cadena Base32 sea un secreto válido sin validación posterior. El formato
interno de `chrome.storage.local` sigue siendo dependiente de la versión de
Chrome y de la extensión.

## Instalación local

Desde la raíz del proyecto:

```powershell
python -m pip install -e .
```

## Diagnóstico del almacenamiento

Usando la ruta por defecto del perfil `Default`:

```powershell
python -m cod_autenticador inspect
```

Indicando explícitamente la ruta:

```powershell
python -m cod_autenticador inspect `
  --profile-dir "$env:LOCALAPPDATA\Google\Chrome\User Data\Default"
```

También se puede indicar directamente el directorio de almacenamiento:

```powershell
python -m cod_autenticador inspect `
  --storage-dir "C:\ruta\Local Extension Settings\bhghoamapcdpbohphigoooaddinpkbai"
```

Para inspeccionar el almacén sincronizado:

```powershell
python -m cod_autenticador inspect --storage-location sync
```

Listar las cuentas detectadas sin imprimir secretos:

```powershell
python -m cod_autenticador accounts --storage-location sync
```

Generar un código desde una cuenta no cifrada validada:

```powershell
python -m cod_autenticador generate-from-storage `
  --storage-location sync `
  --account "identificador_de_cuenta"
```

El resultado es diagnóstico. Antes de usar cualquier secreto encontrado se
debe confirmar la cuenta, el algoritmo, el período, los dígitos y si el valor
está cifrado.

## Generación TOTP

```powershell
python -m cod_autenticador generate `
  --secret "JBSWY3DPEHPK3PXP" `
  --algorithm SHA1 `
  --digits 6 `
  --period 30
```

El secreto no se imprime en logs ni se persiste.

## Integración futura

La interfaz pública prevista es:

```python
from cod_autenticador import MfaCodeService

service = MfaCodeService.from_storage(
    storage_path=ruta_del_almacen_sync,
    account_id="identificador_de_cuenta",
)
code = service.get_code("portal_empresa")
```

Los proveedores de LevelDB, exportación y DevTools se agregarán detrás de esa
interfaz cuando el formato real de la versión instalada haya sido validado.
=======
# autenticador_API
Codigo que permite extraer el codigo de verificación de google chrome para llevar a cabo  automatizaciones.
>>>>>>> 4e13f87b5997244ddb10c2c758aba5bdfe143d32
