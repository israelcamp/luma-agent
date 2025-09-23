from graph import graph

def main():
    response = graph.invoke({
        "input": "Oi"
    })
    print(response)

if __name__ == "__main__":
    main()
