import React, { useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = "http://localhost:8000";

const ActionProvider = ({ createChatBotMessage, setState, children }) => {
  const handleQuery = (message) => {
    // Send a request to the API
    axios.post(`${API_BASE_URL}/chat`, { message })
      .then((response) => {
        const botMessage = createChatBotMessage(`${response.data}`);
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, botMessage],
        }));
      })
      .catch((error) => {
        const botMessage = createChatBotMessage(`Sorry, I could not understand that.`);
        setState((prev) => ({
          ...prev,
          messages: [...prev.messages, botMessage],
        }));
      });
  };
  return (
    <div>
      {React.Children.map(children, (child) => {
        return React.cloneElement(child, {
          actions: { handleQuery},
        });
      })}
    </div>
  );
};

export default ActionProvider;