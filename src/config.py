from pathlib import Path
from dynaconf import Dynaconf

ROOT_DIR = Path(__file__).parent.parent

settings = Dynaconf(
    settings_files=[str(ROOT_DIR / "settings.toml")],
    load_dotenv=True,
    envvar_prefix="CINEMA_EXPERT_AI_AGENT",
    dotenv_path=str(ROOT_DIR / ".env"),
)

OPENAI_API_KEY = settings.get("OPENAI_API_KEY")
MODEL_NAME = settings.get("MODEL_NAME", "gpt-4o-mini")
TEMPERATURE = settings.get("TEMPERATURE", 0.7)
SYSTEM_PROMPT = settings.get("SYSTEM_PROMPT", "")
MAX_TOKENS = settings.get("MAX_TOKENS", 300)

OMDB_API_URL = settings.get("OMDB_API_URL", "http://www.omdbapi.com/")
OMDB_API_KEY = settings.get("OMDB_API_KEY", "")
CSV_DATASET_PATH = str(
    ROOT_DIR / settings.get("CSV_DATASET_PATH", "data/imdb_top_1000.csv")
)
