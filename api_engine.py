import json
from configparser import ConfigParser
from openai import OpenAI

class APIEngine:
    def __init__(self, engine=None):
        """
        Initialize the APIEngine class.

        Args:
            engine (str): Optional. The API engine to use. If not provided, it is read from the config file.
        """
        self.config = self.load_config()
        self.engine_votes = engine if engine else self.config.get('API', 'engine_votes')
        self.api_key = self.get_api_key(self.engine_votes)
        self.default_model = self.get_default_model(self.engine_votes)
        self.allowed_models = self.get_allowed_models(self.engine_votes)
        self.client = None

    def load_config(self):
        """
        Load the configuration from the 'config.ini' file.

        Returns:
            ConfigParser: The configuration object.
        """
        config = ConfigParser()
        config.read('config.ini')
        return config

    def get_api_key(self, engine):
        """
        Retrieve the API key based on the engine type.

        Args:
            engine (str): The API engine.

        Returns:
            str: The API key for the specified engine.

        Raises:
            ValueError: If the engine is unsupported.
        """
        if engine == 'groq':
            return self.config.get('API', 'groq_key')
        elif engine == 'ollama':
            return self.config.get('API', 'ollama_key')
        elif engine == 'openai':
            return self.config.get('API', 'openai_key')
        else:
            raise ValueError(f"Unsupported API engine: {engine}")

    def get_default_model(self, engine):
        """
        Retrieve the default model based on the engine type.

        Args:
            engine (str): The API engine.

        Returns:
            str: The default model for the specified engine.

        Raises:
            ValueError: If the engine is unsupported.
        """
        if engine == 'groq':
            return self.config.get('Models', 'groq_default')
        elif engine == 'ollama':
            return self.config.get('Models', 'ollama_default')
        elif engine == 'openai':
            return self.config.get('Models', 'openai_default')
        else:
            raise ValueError(f"Unsupported API engine: {engine}")

    def get_allowed_models(self, engine):
        """
        Retrieve the allowed models based on the engine type.

        Args:
            engine (str): The API engine.

        Returns:
            list: A list of allowed models for the specified engine.

        Raises:
            ValueError: If the engine is unsupported.
        """
        if engine == 'groq':
            return self.config.get('Models', 'groq_allowed').split(', ')
        elif engine == 'ollama':
            return self.config.get('Models', 'ollama_allowed').split(', ')
        elif engine == 'openai':
            return self.config.get('Models', 'openai_allowed').split(', ')
        else:
            raise ValueError(f"Unsupported API engine: {engine}")

    def initialize_api(self, engine, model):
        """
        Initialize the API client for a specified engine and model.

        Args:
            engine (str): The API engine.
            model (str): The model to be used.
        """
        if engine == 'openai':
            self.client = OpenAI(api_key=self.api_key)

    def test_connection(self, engine=None, model=None):
        """
        Test the connection to the API.

        Args:
            engine (str): Optional. The API engine to test. Defaults to the initialized engine.
            model (str): Optional. The model to test. Defaults to the initialized default model.

        Raises:
            ValueError: If the engine is unsupported or the connection test fails.
        """
        selected_engine = engine if engine else self.engine_votes
        selected_model = model if model else self.default_model
        try:
            if selected_engine == 'groq':
                self._test_groq(selected_model)
            elif selected_engine == 'ollama':
                self._test_ollama(selected_model)
            elif selected_engine == 'openai':
                self._test_openai(selected_model)
            else:
                raise ValueError(f"Unsupported API engine: {selected_engine}")
        except Exception as e:
            raise ValueError(f"Failed to connect to {selected_engine} API: {e}")

    def _test_groq(self, model):
        """
        Test connection to the Groq API.

        Args:
            model (str): The model to be tested.
        """
        from groq import Groq
        client = Groq(api_key=self.api_key)
        client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Test"}],
            temperature=0.5,
            max_tokens=10,
            top_p=0.9,
            stream=False,
            stop=None,
        )

    def _test_ollama(self, model):
        """
        Test connection to the Ollama API.

        Args:
            model (str): The model to be tested.
        """
        import ollama
        ollama.generate(
            model=model,
            prompt="Test",
            options={'temperature': 0.5}
        )

    def _test_openai(self, model):
        """
        Test connection to the OpenAI API.

        Args:
            model (str): The model to be tested.
        """
        completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        _ = completion.choices[0].message.content

    def call_api(self, prompt, engine=None, model=None):
        """
        Call the API with a given prompt.

        Args:
            prompt (dict): The prompt to send to the API.
            engine (str): Optional. The API engine to use. Defaults to the initialized engine.
            model (str): Optional. The model to use. Defaults to the initialized default model.

        Returns:
            str: The response from the API.

        Raises:
            ValueError: If the engine is unsupported.
        """
        selected_engine = engine if engine else self.engine_votes
        selected_model = model if model else self.default_model

        if selected_engine == 'ollama':
            import ollama
            system_message = prompt['messages'][0]['content']
            user_message = prompt['messages'][1]['content']
            combined_message = f"{system_message}\n\n{user_message}"
            response = ollama.generate(
                model=selected_model,
                prompt=combined_message,
                options={'temperature': prompt.get('temperature', 0.5)}
            )
            return response['response'].strip()
        elif selected_engine == 'groq':
            return self._call_groq(prompt, selected_model)
        elif selected_engine == 'openai':
            return self._call_openai(prompt, selected_model)
        else:
            raise ValueError(f"Unsupported API engine: {selected_engine}")

    def _call_groq(self, prompt, model):
        """
        Call the Groq API with a given prompt.

        Args:
            prompt (dict): The prompt to send to the API.
            model (str): The model to use.

        Returns:
            str: The response from the Groq API.
        """
        from groq import Groq
        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            model=model,
            messages=prompt['messages'],
            temperature=prompt.get('temperature', 0.5),
            max_tokens=prompt.get('max_tokens', 4096),
            top_p=prompt.get('top_p', 0.9),
            stream=False,
            stop=None,
        )
        return response.choices[0].message.content.strip()

    def _call_openai(self, prompt, model):
        """
        Call the OpenAI API with a given prompt.

        Args:
            prompt (dict): The prompt to send to the API.
            model (str): The model to use.

        Returns:
            str: The response from the OpenAI API.
        """
        self.client = OpenAI(api_key=self.api_key)
        response = self.client.chat.completions.create(
            model=model,
            messages=prompt['messages'],
            temperature=prompt.get('temperature', 0.5),
            max_tokens=prompt.get('max_tokens', 4096)
        )
        return response.choices[0].message.content.strip()

    def transcribe_audio(self, file_path, prompt=None, response_format="json", language=None, temperature=0.0):
        from groq import Groq
        client = Groq(api_key=self.api_key)
        with open(file_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(file_path, file.read()),
                model="whisper-large-v3",
                prompt=prompt,
                response_format=response_format,
                language=language,
                temperature=temperature
            )
        return transcription.text