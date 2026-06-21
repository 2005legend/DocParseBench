def parse(pdf_path):
    import os
    os.environ["LLAMA_CLOUD_API_KEY"] = "llx-DFfnyUVEHlXUH3e9Ye0yIt0vphhqQDpa2dugJTJuSC1Ml4mB"
    from llama_parse import LlamaParse
    parser = LlamaParse(result_type="markdown")
    documents = parser.load_data(pdf_path)
    return "\n\n".join([doc.text for doc in documents])
