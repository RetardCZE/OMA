import os
import openai
from typing import List
import json
import pandas as pd
from OMPython import OMCSessionZMQ
from openai.types.chat import (ChatCompletionUserMessageParam,
                               ChatCompletionSystemMessageParam,
                               ChatCompletionToolMessageParam,
                               ChatCompletionAssistantMessageParam)

from plot import plot
from example_tube import default_model

tools = [
    {
      'type': 'function',
      'function': {
        'name': 'update_code',
        "description": "Update code in the viewport and related icon and diagram visualisation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "new_code": {
                        "type": "string",
                        "description": "The new OpenModelica model code.",
                    },
                },
                "required": ["new_code"],
            },
        }
    },
]


class Agent:
    def __init__(self):
        os.environ['OPENAI_API_KEY'] = "sk-proj-LkWi42fLMjO7QuUWbpY2T3BlbkFJDvjVluSMPTcAssyTYNev"
        self.client = openai.Client(api_key=os.environ['OPENAI_API_KEY'])
        self.messages: List[ChatCompletionUserMessageParam |
                            ChatCompletionAssistantMessageParam |
                            ChatCompletionToolMessageParam |
                            ChatCompletionSystemMessageParam] = []

        self.waiting_messages: List[ChatCompletionSystemMessageParam] = []
        self.update_code(default_model)

    def update_code(self, new_code: str) -> str:
        self.code = new_code
        self.add_system_message("New code:" + self.code, True)
        try:
            self.icon_view, self.diagram_view = plot(self.code)
            return "Code and views were updated successfully."
        except Exception as e:
            return "Code updated. Could not update views due to error: " + str(e)

    def add_user_message(self, content: str) -> None:
        if self.waiting_messages:
            for message in self.waiting_messages:
                self.messages.append(message)
            self.waiting_messages = []
        user_msg = ChatCompletionUserMessageParam(role='user', content=content)
        self.messages.append(user_msg)


    def add_system_message(self, content: str, wait: bool = False) -> None:
        system_msg = ChatCompletionSystemMessageParam(role='system', content=content)
        if wait:
            self.waiting_messages.append(system_msg)
        else:
            self.messages.append(system_msg)

    def simulate(self, stop_time=10, number_of_intervals=500, output_format="csv", variable_filter=None):
        model_string = self.code
        # Create an OMC session
        omc = OMCSessionZMQ()

        # Properly escape the model string for loading
        model_string_escaped = model_string.replace('"', '\\"').replace('\n', '\\n')

        # Load the model string into OpenModelica
        load_result = omc.execute(f'loadString("{model_string_escaped}")')
        if not load_result:
            raise Exception("Failed to load model string")

        # Extract the model name from the string (assuming the first line contains "model ModelName")
        model_name = model_string.split()[1]

        # Check if the model is loaded successfully
        check_model = omc.execute(f'isModel("{model_name}")')
        if not check_model:
            raise Exception(f"Model {model_name} does not exist! Please load it first before simulation.")

        # Build the simulate command
        simulate_command = f"simulate({model_name}, stopTime={stop_time}, numberOfIntervals={number_of_intervals}, outputFormat=\"{output_format}\""
        if variable_filter:
            simulate_command += f", variableFilter=\"{variable_filter}\""
        simulate_command += ")"

        # Run the simulation
        result = omc.execute(simulate_command)

        # Check if the simulation was successful
        if "Simulation Failed" in result:
            raise Exception(result)

        # Load the results
        result_file = f"{model_name}_res.{output_format}"
        if output_format == "csv":
            df = pd.read_csv(result_file)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        return df
    def run(self):
        while self.messages[-1]['role'] != 'assistant':
            response = self.client.chat.completions.create(
                model='gpt-4o',
                messages=self.messages,
                tool_choice='auto',
                tools=tools
            )

            message = response.choices[0].message
            content = message.content
            tool_calls = message.tool_calls

            ast_msg = ChatCompletionAssistantMessageParam(role='assistant', content=content, tool_calls=tool_calls)
            self.messages.append(ast_msg)

            if tool_calls:
                for tool in tool_calls:
                    callId = tool.id
                    tool_response = str(eval(f'self.{tool.function.name}')(**json.loads(tool.function.arguments)))
                    tool_msg = ChatCompletionToolMessageParam(role='tool', tool_call_id=callId, content=tool_response)
                    self.messages.append(tool_msg)


