from dataclasses import dataclass


@dataclass(frozen=True)
class Version:
    ts: int  # milliseconds
    seq: int  # counter

    @classmethod
    def from_stream_id(cls, sid: str) -> "Version":
        """Construct new `Version` object from stream_id: `timestamp`-`seq`."""
        ts, seq = map(int, sid.split("-", 1))
        return cls(ts, seq)

    def to_stream_id(self) -> str:
        return f"{self.ts}-{self.seq}"

    def __gt__(self, version: "Version"):
        return not (
            self.ts < version.ts or (version.ts == self.ts and self.seq <= version.seq)
        )
