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

            const response = await fetch('http://localhost:5000/openai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ text: inputText }),
            });
    
    
            this.setState({
                messages: [...messages, newMessage, { id: messages.length + 2, text: response }],
                inputText: ''
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