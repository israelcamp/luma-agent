from graph import graph

def main():
    response = graph.invoke({
        "input": "Hello"
    })
    print(response)

if __name__ == "__main__":
    main()
