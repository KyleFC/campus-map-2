import React from 'react';

async function sendUserInput(userInput) {
    try {
        const response = await fetch('/api/openai/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Include other headers as needed, such as Authorization for JWT tokens
            },
            body: JSON.stringify({ userInput: userInput })
        });
        const data = await response.json();
        // console.log(data.finalOutput);
        return data.finalOutput;
        // You can now use the finalOutput from Django in your React component
    } catch (error) {
        console.error('Error:', error);
    }
}

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
            sendUserInput(inputText)
                .then(response => {
                    // Directly push new message for debugging
                    console.log(response);
                    this.setState(prevState => ({
                        messages: [...prevState.messages, { id: prevState.messages.length + 1, text: inputText }, { id: prevState.messages.length + 2, text: response }],
                        inputText: ''
                    }));
                })
            
                .catch(error => {
                    console.error('Error:', error);
                });
        }
    }

    render() {
        const { messages, inputText } = this.state;

        return (
            <div className="chatwindow">
                <ul>
                    {messages.map((message) => (
                        <li key={message.id}>{message.text}</li>
                    ))}
                </ul>
                <form className="chatbox" onSubmit={this.handleSubmit}>
                    <input
                        id="martychat"
                        type="text"
                        value={inputText}
                        placeholder="Ask Marty a question..."
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