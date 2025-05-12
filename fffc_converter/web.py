import gradio as gr
from converter import FixedFileFormatConverter
from tempfile import NamedTemporaryFile


def convert(input_file_path, metadata_file_path):
    try:
        converter = FixedFileFormatConverter(metadata_file_path)
        with (
            open(input_file_path.name, "r", encoding="utf-8") as input_file,
            NamedTemporaryFile(
                delete=False, prefix="data_", suffix=".csv"
            ) as temp_file,
            NamedTemporaryFile(
                delete=False, prefix="error_", suffix=".txt"
            ) as error_file,
        ):
            for csv_line, error_line in converter.convert(input_file):
                if csv_line:
                    temp_file.write(csv_line.encode())
                if error_line:
                    error_file.write(error_line.encode())
            temp_file.seek(0)
            error_file.seek(0)
            output_csv = temp_file.name
            error_txt = error_file.name
        return output_csv, error_txt
    except Exception as e:
        raise gr.Error(
            "An error occurred during conversion: " + str(e),
            duration=5,
        )


server = gr.Interface(
    fn=convert,
    inputs=[
        gr.File(label="Fichier de données"),
        gr.File(label="Fichier de métadonnées"),
    ],
    outputs=[
        gr.File(label="Fichier CSV de sortie"),
        gr.File(label="Fichier d'erreurs"),
    ],
    title="Convertisseur de formats de fichiers fixes",
    description="Convertit un fichier de données à format fixe en CSV en utilisant un fichier de métadonnées.",
    theme="soft",
    css="""
h1 {
    text-align: left!important;
}
""",
    allow_flagging="never",
    submit_btn="Convertir",
    clear_btn="Effacer",
    api_name="convert",
)
server.launch()
