from handlers.citation_upload_handler import CitationUploadHandler

def main():
    print("Hello from comp-data-group-project!")
    # Create an instance of the citation upload handler
    
    
    handler = CitationUploadHandler()
    handler.setDbPathOrUrl("http://localhost:9999/blazegraph/sparql")
    handler.pushDataToDb("")

if __name__ == "__main__":
    main()
