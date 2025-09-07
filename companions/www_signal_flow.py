# Signal Flow: Internet → Handshake → Prime → Harmonize → Forward
import os
from openai import OpenAI

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
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
)

completion = client.chat.completions.create(
    model="openai/gpt-oss-20b:together",
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?"
        }
    ],
)

print(completion.choices[0].message)

import asyncio
import aiohttp
from pyzmq import asyncio as azmq
import pydantic
import orjson


class SwarmNode:
    def __init__(self):
        self.context = azmq.Context()
        self.input_socket = self.context.socket(azmq.PULL)    # Receive signals
        self.output_socket = self.context.socket(azmq.PUSH)   # Forward signals
        self.coordination_socket = self.context.socket(azmq.REQ) # Swarm sync
    
    async def signal_handler(self, raw_signal):
        # Step 1: Handshake
        if not await self.handshake(raw_signal):
            return self.drop_signal(raw_signal)
        
        # Step 2: Prime check
        if await self.is_primed(raw_signal):
            return await self.forward_signal(raw_signal)
        
        # Step 3: Harmonize then forward
        harmonized = await self.harmonize(raw_signal)
        return await self.forward_signal(harmonized)
    
    async def handshake(self, signal):
        # Verify signal integrity, source, format
        return pydantic.validate(signal, SignalSchema)
    
    async def is_primed(self, signal):
        # Check if signal is already in optimal format
        return signal.get('harmonized', False)
    
    async def harmonize(self, signal):
        # Transform signal to swarm-optimal format
        # Apply filters, normalize, enrich
        signal['harmonized'] = True
        signal['node_id'] = self.node_id
        signal['timestamp'] = time.time()
        return signal
    
    async def forward_signal(self, signal):
        # Send to next node in swarm or external destination
        await self.output_socket.send(orjson.dumps(signal))
