
def get_human_feedback(state: dict) -> str:
    print("\n--- HUMAN REVIEW ---")
    print("\nDraft:\n")
    print(state.get("draft", ""))

    print("\nEditor feedback:")
    for item in state.get("editor_feedback", []):
        print(f"- {item}")

    return input(
        "\nEnter feedback, or type 'approve' to accept: "
    ).strip()
