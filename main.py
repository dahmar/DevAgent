from agent import ask_agent


while True:
    user_input = input("\nТы: ")
    if user_input.strip().lower() == "exit":
        break

    result = ask_agent(user_input)

    print("\nAgent:")
    print(repr(result))
