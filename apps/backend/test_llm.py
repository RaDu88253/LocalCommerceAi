from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline

print("--- Initializing local LLM (flan-t5-base)... ---")
print("This may take a moment and will download the model on the first run.")

try:
    # Initialize the same local LLM used in the agent graph
    local_llm = HuggingFacePipeline.from_model_id(
        model_id="google/flan-t5-base",
        task="text2text-generation",
        pipeline_kwargs={"max_new_tokens": 150} # A bit longer for general chat
    )
    print("\n--- ✅ LLM Initialized. You can now chat with the model. ---")
    print("--- Type 'exit' or 'quit' to end the session. ---\n")

    while True:
        # Get input from the user
        user_input = input("You > ")

        # Check for exit command
        if user_input.lower() in ['exit', 'quit']:
            print("Exiting chat. Goodbye!")
            break

        # Get response from the LLM
        response = local_llm.invoke(user_input)

        # Print the LLM's response
        print(f"LLM > {response}")

except Exception as e:
    print(f"\n--- ❌ FAILED to initialize or run the LLM ---")
    print(f"Error: {e}")
    print("Please ensure you have 'transformers' and 'torch' installed (`pip install -r requirements.txt`).")
