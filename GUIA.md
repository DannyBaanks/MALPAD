# GUIA.md — MALPAD para el que lo opera

Guía humana. Cada comando está ejecutado, con salida real.

## 1. El comando que viniste a buscar

```powershell
py -m pytest tests -q
```

## 2. La regla de oro

**Si el adapter tuvo que "entender" qué edición hacer, ya hicimos trampa.**
Malbolge decide qué editar; el host solo transporta y materializa lo autorizado.

## 3. Antes de empezar

Usa `py`, no `python` (el `python` desnudo puede estar shim-eliminado y morir con
exit 2718). Desde la raíz de `MALPAD\`.

## 4. Comandos, con salida real

### Correr los tests de contrato (M0)

```powershell
py -m pytest tests -q
```

Salida real (última línea):

```
..................                                                       [100%]
18 passed in 0.35s
```

### Ver el flujo de eventos del demo (el oracle de contrato)

```powershell
py tools/editor_ir.py
```

Salida real (fragmento — primer demo):

```
@MALPAD:BOOT
@MALPAD:CHAR:72
@MALPAD:CHAR:69
@MALPAD:CHAR:76
@MALPAD:CHAR:76
@MALPAD:CHAR:79
@MALPAD:MOVE:4:0
@MALPAD:MOVE:3:0
...
```

La última línea de stderr da el estado final:

```
FINAL {'buffer': 'HEAMALBOLGELO', 'buffer_len': 13, 'cursor': 11, 'row': 0, 'state': 'HALTED'}
```

### Correr un script de teclas guardado

```powershell
py tools/editor_ir.py tests\fixtures\keystrokes\demo.keys.bin
```

Emite los eventos `@MALPAD:` que produciría el editor para ese script.

## 5. Cómo leer la salida

| Frame | Qué significa |
|-------|---------------|
| `@MALPAD:CHAR:<b>` | el core decidió insertar el byte `<b>` |
| `@MALPAD:MOVE:<c>:<r>` | el core decidió la posición lógica del cursor |
| `@MALPAD:LINE:<r>:<text>` | el core decidió renderizar esa línea |
| `@MALPAD:SAVE` | el core pide guardar (sin autoridad; el host decide) |
| `@MALPAD:SAVED` / `SAVE_DENIED` / `SAVE_ERROR` | respuesta del host al save |
| `@MALPAD:QUIT` | el core termina limpio |
| `@MALPAD:ERR:...` | error defensivo (byte inválido, buffer lleno, no acepta input) |

## 6. Trampas

- **`python` muere (exit 2718).** Usa `py`.
- **Los fixtures de teclas son bytes crudos** (`.keys.bin`), contienen bytes de
  control. No los abras como texto UTF-8; están bien así.
- **`tools/editor_ir.py` es el oracle de construcción, no la lógica que
  enviaremos.** El claim real (M2+) es que el espécimen Malbolge ejecute lo mismo
  y se valide en intérpretes independientes. El IR no se auto-valida.
- **`editor_ir.py` con `HALTED` ignora el resto del input.** Esa es la semántica
  congelada (T17).
- **El demo termina en `HEAMALBOLGELO`, no `HELAOMALBOLGE`.** El estado es
  determinista; no "corrijas" el fixture para que se vea más bonito.