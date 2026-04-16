import asyncio
import os
import dotenv
from backboard import BackboardClient

dotenv.load_dotenv()

async def main():
    api_key = os.getenv("BACKBOARD_API_KEY")
    client = BackboardClient(api_key=api_key)

    # 1. Create a specialized Assistant
    assistant = await client.create_assistant(
        name="Document Assistant",
        system_prompt="You are a helpful document analysis assistant. Answer questions based ONLY on the provided document."
    )

    # 2. Upload the PDF (Make sure 'my_document.pdf' is in your folder!)
    # This sends the file to Backboard to be "read" and "indexed"
    document = await client.upload_document_to_assistant(
        assistant.assistant_id,
        "my_document.pdf"
    )
    print("Waiting for document to be indexed...")

    # 3. Wait for the AI to finish "reading" the file
    while True:
        status = await client.get_document_status(document.document_id)
        if status.status == "indexed":
            print("✅ Document indexed successfully!")
            break
        elif status.status == "failed":
            print(f"❌ Document indexing failed: {status.status_message}")
            return
        await asyncio.sleep(2)

    # 4. Start the conversation
    thread = await client.create_thread(assistant_id=assistant.assistant_id)
    
    print("🤖 Assistant is thinking...")
    
    # 5. Ask the question with Streaming enabled
    async for chunk in await client.add_message(
        thread_id=thread.thread_id,
        content="What are the key points in the uploaded document?",
        stream=True
    ):
        if chunk.get("type") == "content_streaming":
            content = chunk.get("content", "")
            if content:
                print(content, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    asyncio.run(main())