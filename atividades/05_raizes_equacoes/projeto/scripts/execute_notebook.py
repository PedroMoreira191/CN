"""Executor sequencial de notebook sem kernel ou sockets locais.

Usado apenas para validação no sandbox. O arquivo resultante continua sendo um
notebook Jupyter/Colab padrão.
"""

from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import io
import os
import traceback
from pathlib import Path

import nbformat


def _normalizar_mime(valor):
    if isinstance(valor, bytes):
        return base64.b64encode(valor).decode("ascii")
    return valor


def _mimebundle(objeto):
    dados = {}
    metadata = {}

    if hasattr(objeto, "_repr_mimebundle_"):
        bundle = objeto._repr_mimebundle_(include=None, exclude=None)
        if isinstance(bundle, tuple):
            bundle, metadata = bundle
        if bundle:
            dados.update({chave: _normalizar_mime(valor) for chave, valor in bundle.items()})

    if "text/html" not in dados and hasattr(objeto, "_repr_html_"):
        html = objeto._repr_html_()
        if html is not None:
            dados["text/html"] = html

    dados.setdefault("text/plain", repr(objeto))
    return dados, metadata


def _executar_codigo(source, namespace, nome_celula):
    arvore = ast.parse(source, filename=nome_celula, mode="exec")
    ultima_expressao = None
    if arvore.body and isinstance(arvore.body[-1], ast.Expr):
        ultima_expressao = ast.Expression(arvore.body.pop().value)

    if arvore.body:
        exec(compile(arvore, nome_celula, "exec"), namespace)
    if ultima_expressao is not None:
        return eval(compile(ultima_expressao, nome_celula, "eval"), namespace)
    return None


def execute_notebook(path, cwd=None):
    path = Path(path).resolve()
    cwd = Path(cwd).resolve() if cwd else path.parent
    notebook = nbformat.read(path, as_version=4)
    namespace = {"__name__": "__main__"}
    original_cwd = Path.cwd()

    try:
        os.chdir(cwd)
        contador = 0
        for indice, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue

            contador += 1
            cell.execution_count = contador
            cell.outputs = []
            stdout = io.StringIO()
            displays = []

            def capturar_display(*objetos, **_):
                for objeto in objetos:
                    dados, metadata = _mimebundle(objeto)
                    displays.append(
                        nbformat.v4.new_output(
                            "display_data", data=dados, metadata=metadata
                        )
                    )

            if "display" in namespace:
                namespace["display"] = capturar_display

            try:
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
                    resultado = _executar_codigo(
                        cell.source, namespace, f"<cell-{indice + 1}>"
                    )
                if "display" in namespace:
                    namespace["display"] = capturar_display
            except Exception as erro:
                texto = stdout.getvalue()
                if texto:
                    cell.outputs.append(
                        nbformat.v4.new_output("stream", name="stdout", text=texto)
                    )
                cell.outputs.append(
                    nbformat.v4.new_output(
                        "error",
                        ename=type(erro).__name__,
                        evalue=str(erro),
                        traceback=traceback.format_exc().splitlines(),
                    )
                )
                nbformat.write(notebook, path)
                raise

            texto = stdout.getvalue()
            if texto:
                cell.outputs.append(
                    nbformat.v4.new_output("stream", name="stdout", text=texto)
                )
            cell.outputs.extend(displays)
            if resultado is not None:
                dados, metadata = _mimebundle(resultado)
                cell.outputs.append(
                    nbformat.v4.new_output(
                        "execute_result",
                        data=dados,
                        metadata=metadata,
                        execution_count=contador,
                    )
                )

        nbformat.validate(notebook)
        nbformat.write(notebook, path)
        return path
    finally:
        os.chdir(original_cwd)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--cwd", type=Path)
    args = parser.parse_args()
    print(execute_notebook(args.notebook, cwd=args.cwd))


if __name__ == "__main__":
    main()
