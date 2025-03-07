import "./styles.css";
import "leaflet/dist/leaflet.css";
import axios from "axios";
import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup, Circle } from "react-leaflet";
import { Icon } from "leaflet";

import Chatbot from 'react-chatbot-kit';
import 'react-chatbot-kit/build/main.css';
import config from './bot/config';
import ActionProvider from "./bot/ActionProvider";
import MessageParser from "./bot/MessageParser";



const BASE_API_URL = "http://localhost:8000";
const RADIUS = 5000; // 5km

// Create custom icons
const outlineIcon = new Icon({
  iconUrl: require("./icons/outline.png"),
  iconSize: [38, 38] // size of the icon
});

const filledIcon = new Icon({
  iconUrl: require("./icons/filled.png"),
  iconSize: [38, 38] // size of the icon
});

export default function App() {
  const [markers, setMarkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mapCenter, setMapCenter] = useState([3.1088204, 101.7068227]);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [chatbotVisible, setChatbotVisible] = useState(false);

  // Fetch all the outlets
  useEffect(() => {
    axios.get(`${BASE_API_URL}/outlets`)
      .then(response => {
        const outlets = response.data;
        console.log(outlets);
        const newMarkers = outlets.map(outlet => {
          const latitude = parseFloat(outlet.latitude);
          const longitude = parseFloat(outlet.longitude);
          if (isNaN(latitude) || isNaN(longitude)) {
            console.error(`Invalid latitude or longitude for outlet ${outlet.id}`);
            return null;
          }
          return {
            id: outlet.id,
            geocode: [latitude, longitude],
            name: outlet.name,
            address: outlet.address,
            operatingHours: outlet.operating_hours,
            intersects: false
          };
        }).filter(marker => marker !== null);

        setMarkers(newMarkers);
        if (newMarkers.length > 0) {
          setMapCenter(newMarkers[0].geocode);
        }
        setLoading(false);
      })
      .catch(error => {
        console.error("There was an error fetching the outlets!", error);
        setLoading(false);
      });
  }, []);

  // Toggle when maerker is clicked
  const handleMarkerClick = (markerId) => {
    if (selectedMarker === markerId) {
      setSelectedMarker(null);
      setMarkers(markers.map(marker => ({ ...marker, intersects: false })));
    } else {
      setSelectedMarker(markerId);
      const selected = markers.find(marker => marker.id === markerId);
      const updatedMarkers = markers.map(marker => {
        const distance = getDistance(selected.geocode, marker.geocode);
        return {
          ...marker,
          intersects: distance <= RADIUS
        };
      });
      setMarkers(updatedMarkers);
    }
  };

  // Toggle for chatbot
  const toggleChatbot = () => {
    setChatbotVisible(!chatbotVisible);
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div style={{display: 'flex', flexDirection: 'row', height: '100vh'}}>
      <MapContainer center={mapCenter} zoom={14}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {markers.map((marker) => (
          <React.Fragment key={marker.id}>
            <Marker
              position={marker.geocode}
              icon={marker.intersects ? filledIcon : outlineIcon}
              eventHandlers={{
                click: () => handleMarkerClick(marker.id),
              }}
            >
              <Popup>
                <div>
                  <strong>{marker.name}</strong> <br />
                  {marker.address} <br />
                  {marker.operatingHours}
                </div>
              </Popup>
            </Marker>
            {selectedMarker === marker.id && (
              <Circle
                center={marker.geocode}
                radius={RADIUS}
                color="#2898ec"
              />
            )}
          </React.Fragment>
        ))}

        
      </MapContainer>
      <button onClick={toggleChatbot} className="chatbot-toggle-button">
      </button>
      <div className={`chatbot-container ${chatbotVisible ? '' : 'hidden'}`}>
        <Chatbot
          config={config}
          messageParser={MessageParser}
          actionProvider={ActionProvider}
        />
      </div>

    </div>
  );
}

// Function to calculate the distance between two coordinates in meters
function getDistance(coord1, coord2) {
  const R = 6371e3; // Earth's radius in meters
  const lat1 = coord1[0] * Math.PI / 180;
  const lat2 = coord2[0] * Math.PI / 180;
  const deltaLat = (coord2[0] - coord1[0]) * Math.PI / 180;
  const deltaLon = (coord2[1] - coord1[1]) * Math.PI / 180;

  const a = Math.sin(deltaLat / 2) * Math.sin(deltaLat / 2) +
            Math.cos(lat1) * Math.cos(lat2) *
            Math.sin(deltaLon / 2) * Math.sin(deltaLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));

  return R * c;
}