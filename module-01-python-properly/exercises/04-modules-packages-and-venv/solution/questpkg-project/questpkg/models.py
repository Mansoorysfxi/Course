class Quest:
    def __init__(
        self,
        name: str,
        difficulty: str,
        reward_gold: int,
        is_complete: bool = False,
    ) -> None:
        self.name: str = name
        self.difficulty: str = difficulty
        self.reward_gold: int = reward_gold
        self.is_complete: bool = is_complete

    def __repr__(self) -> str:
        return (
            f"Quest(name={self.name!r}, difficulty={self.difficulty!r}, "
            f"reward_gold={self.reward_gold}, is_complete={self.is_complete})"
        )
