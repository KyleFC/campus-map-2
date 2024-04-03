import React from 'react';

class MartyChat extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            messages: [],
            inputText: ''
        };
    }

    handleSubmit = async (event) => {
        event.preventDefault();
        const { inputText, messages } = this.state;
        if (inputText.trim() !== '') {
            const newMessage = {
                id: messages.length + 1,
                text: inputText
            };

            // Make a POST request to the OpenAI API
            const response = await fetch('https://api.openai.com/v1/engines/davinci-codex/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer YOUR_API_KEY' // Replace with your OpenAI API key
                    // get openai api key from secure
                },
                body: JSON.stringify({
                    prompt: inputText,
                    max_tokens: 50 // Adjust the number of tokens as needed
                })
            });

            const data = await response.json();
            const generatedText = data.choices[0].text.trim();

            this.setState({
                messages: [...messages, newMessage, { id: messages.length + 2, text: generatedText }],
                inputText: ''
            });
        }
    }

    render() {
        const { messages, inputText } = this.state;

        return (
            <div>
                <ul>
                    {messages.map((message) => (
                        <li key={message.id}>{message.text}</li>
                    ))}
                </ul>
                <form onSubmit={this.handleSubmit}>
                    <input
                        type="text"
                        value={inputText}
                        placeholder="Search for locations..."
                        style={{ width: '100%', padding: '10px' }}
                        onChange={(event) => this.setState({ inputText: event.target.value })}
                    />
                    <button type="submit">Send</button>
                </form>
            </div>
        );
    }
}

export default MartyChat;