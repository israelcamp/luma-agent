import sys

from rich import print

from graph import State, graph


def main():
    state = State(
        authenticated=True,
    )
    while True:
        user_input = input("Message: ")
        if user_input == "quit":
            sys.exit(0)

        state["input"] = user_input
        response = graph.invoke(state)

        answer = response.pop("answer")
        print(response)
        print("== ANSWER == ", "\n", answer)

        state.update(response)
        state.update({"stop": False, "input": None})


if __name__ == "__main__":
    main()
