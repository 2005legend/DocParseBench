def parse(pdf_path):
    import liteparse
    parser = liteparse.Parser()
    doc = parser.parse_file(pdf_path)
    text = ""
    for page in doc.pages:
        for block in page.blocks:
            for line in block.lines:
                text += line.text + "\n"
    return text
