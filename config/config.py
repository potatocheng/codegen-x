from typing import Optional, Dict, Any, List
from pathlib import Path
import toml
from llm.message import Message
from thinking_graph import ThoughtNode

_config_cache: Dict[str, Any] = {}
_config_loaded = False

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """ Load configuration """
    global _config_cache, _config_loaded

    if _config_loaded:
        return _config_cache
    
    if config_path is None:
        config_path = str(Path(__file__).parent / "prompts.toml")

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            _config_cache = toml.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    except toml.TomlDecodeError as e:
        raise ValueError(f"Error decoding TOML file: {e}")

    _config_loaded = True
    return _config_cache

def get_prompts(prompt_name: str) -> Dict[str, str]:
    config = load_config()
    return config[prompt_name]

def format_messages(prompt_name: str, thought_node: ThoughtNode) -> List[Message]:
    """
    Format messages for LLM call based on the prompt name and node.
    
    :param prompt_name: The name of the prompt to use.
    :param node: The ThoughtNode containing component information.
    :return: A list of formatted messages.
    """
    prompts = get_prompts(prompt_name)
    system_message = prompts.get('system', '')

    dependencies = 'None'
    if thought_node.metadata is not None and 'dependencies' in thought_node.metadata:
        dependencies = ', '.join(thought_node.metadata['dependencies'])

    user_message = prompts.get('user', '').format(
        component=thought_node.component,
        description=thought_node.description,
        dependencies = dependencies
    )
    
    return [
       Message(role = "system", content = system_message),
       Message(role = "user", content = user_message)
    ]
    