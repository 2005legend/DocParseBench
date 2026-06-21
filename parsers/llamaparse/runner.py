def parse(pdf_path):
    import os
    from dotenv import load_dotenv
    load_dotenv()
    # os.environ["LLAMA_CLOUD_API_KEY"] should now be loaded from .env
    from llama_parse import LlamaParse
    parser = LlamaParse(result_type="markdown")
    documents = parser.load_data(pdf_path)
    return "\n\n".join([doc.text for doc in documents])
