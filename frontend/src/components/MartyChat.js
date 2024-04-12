import React from 'react';

async function sendUserInput(userInput) {
    try {

        let chatHistory = JSON.parse(localStorage.getItem('chatHistory')) || [];

        //add user and bot messages to chat history
        chatHistory.push({ "role": "user", "content": userInput });
        console.log(chatHistory);

        const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}api/openai/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({chatHistory: chatHistory})
        });
        
        const data = await response.json();
        
        //save to local browser storage
        localStorage.setItem('chatHistory', data.chatHistory);
        console.log(data.chatHistory);
        // console.log(data.finalOutput);

        return data.finalOutput;
    } catch (error) {
        console.error('Error:', error);
    }
}

class MartyChat extends React.Component {
    //if componenet mounted then clear local storage
    componentDidMount() {
        localStorage.removeItem('chatHistory');
    }
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
            /* const newMessage = {
                id: messages.length + 1,
                text: inputText
            }; */
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