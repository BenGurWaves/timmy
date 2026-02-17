import argparse
import logging
from config import config
from agent import Agent

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[
    logging.FileHandler(config.LOG_FILE),
    logging.StreamHandler()
])

def main():
    parser = argparse.ArgumentParser(description="Timmy: A local AI agent.")
    parser.add_argument("--model", type=str, default=config.OLLAMA_MODEL, help="Ollama model to use (e.g., llama3, mistral).")
    args = parser.parse_args()

    logging.info(f"Starting Timmy with model: {args.model}")

    agent = Agent(model_name=args.model)

    print("\nWelcome to Timmy! Type 'exit' to quit.\n")
    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            print("Timmy: ", end="")
            for chunk in agent.stream_response(user_input):
                print(chunk, end="")
            print() # Newline after streaming


        except KeyboardInterrupt:
            print("\nExiting Timmy.")
            break
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print(f"Timmy: Oops! Something went wrong. Check the logs for details.")

if __name__ == "__main__":
    main()
