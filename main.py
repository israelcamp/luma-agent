import sys

from graph import graph


def main():
    while True:
        user_input = input("Message: ")
        if user_input == "quit":
            sys.exit(0)

        response = graph.invoke({
            "input": user_input,
        })

        print(response)

if __name__ == "__main__":
    main()
