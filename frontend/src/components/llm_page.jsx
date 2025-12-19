import React, { useState, useEffect, useRef } from 'react';
import {
  Send, Loader2, MessageSquare, Leaf, Menu, X, Upload, ImagePlus,
  Mic, MicOff, Volume2, Play, Pause // New Icons
} from 'lucide-react';

const KrishiMitra = () => {
  const [language, setLanguage] = useState('English');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [threadId] = useState(() => `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [waitingForImage, setWaitingForImage] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [pendingImageQuery, setPendingImageQuery] = useState(null);
  const [imageQueryInput, setImageQueryInput] = useState('');

  // --- NEW STATES for STT/TTS ---
  const [isRecording, setIsRecording] = useState(false);
  const [isAudioLoading, setIsAudioLoading] = useState(false);
  const [currentPlayingMessageId, setCurrentPlayingMessageId] = useState(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioPlayerRef = useRef(null);
  // ---

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const API_BASE_URL = 'http://localhost:8000';
  const hasInitialized = useRef(false);

  const TEXT = {
    welcome_message: {
      English: "Namaste! I'm your farming assistant. Ask me about crops, schemes, weather, or any agricultural advice.",
      Hindi: "नमस्ते! मैं आपका कृषि सहायक हूँ। मुझसे फसलों, योजनाओं, मौसम या कृषि सलाह के बारे में पूछें।"
    },
    chat_placeholder: {
      English: "Ask about crops, schemes, weather...",
      Hindi: "फसलों, योजनाओं, मौसम के बारे में पूछें..."
    },
    thinking: {
      English: "Thinking...",
      Hindi: "सोच रहा हूँ..."
    },
    error: {
      English: "Sorry, I couldn't process your request. Please try again.",
      Hindi: "क्षमा करें, मैं आपका अनुरोध संसाधित नहीं कर सका। कृपया पुनः प्रयास करें।"
    },
    sidebar_title: {
      English: "KrishiMitra Assistant",
      Hindi: "कृषिमित्र सहायक"
    },
    capabilities: {
      English: "What I can help with:",
      Hindi: "मैं किसमें मदद कर सकता हूँ:"
    },
    features: {
      English: [
        "🌾 Crop planning & advice",
        "🏛️ Government schemes",
        "🌤️ Weather forecasts",
        "💰 Market prices",
        "🔬 Disease diagnosis",
        "💧 Water management"
      ],
      Hindi: [
        "🌾 फसल योजना और सलाह",
        "🏛️ सरकारी योजनाएं",
        "🌤️ मौसम का पूर्वानुमान",
        "💰 बाजार मूल्य",
        "🔬 रोग निदान",
        "💧 जल प्रबंधन"
      ]
    },
    quick_questions: {
      English: "Quick Questions:",
      Hindi: "त्वरित प्रश्न:"
    },
    suggestions: {
      English: [
        "What crops are best for this season?",
        "Tell me about PM-KISAN scheme",
        "Check my plant for diseases",
        "Current market prices for wheat"
      ],
      Hindi: [
        "इस मौसम के लिए कौन सी फसलें सबसे अच्छी हैं?",
        "मुझे पीएम-किसान योजना के बारे में बताएं",
        "मेरे पौधे में बीमारी की जांच करें",
        "गेहूं के वर्तमान बाजार मूल्य"
      ]
    },
    upload_prompt: {
      English: "Please upload an image of the affected plant leaf:",
      Hindi: "कृपया प्रभावित पौधे की पत्ती की तस्वीर अपलोड करें:"
    },
    upload_button: {
      English: "Choose Image",
      Hindi: "तस्वीर चुनें"
    },
    analyze_button: {
      English: "Analyze Plant",
      Hindi: "पौधे का विश्लेषण करें"
    },
    image_selected: {
      English: "Image selected. Click 'Analyze Plant' to diagnose.",
      Hindi: "तस्वीर चुनी गई। निदान के लिए 'पौधे का विश्लेषण करें' पर क्लिक करें।"
    },
    image_query_placeholder: {
      English: "What's the issue? (e.g., 'What are these spots?')",
      Hindi: "क्या समस्या है? (जैसे, 'ये धब्बे क्या हैं?')"
    },
    // --- NEW TEXT ---
    stt_error: {
      English: "Sorry, I couldn't understand the audio. Please try again.",
      Hindi: "क्षमा करें, मैं ऑडियो समझ नहीं सका। कृपया पुनः प्रयास करें।"
    },
    tts_error: {
      English: "Sorry, I couldn't play the audio.",
      Hindi: "क्षमा करें, मैं ऑडियो नहीं चला सका।"
    },
    recording: {
      English: "Recording...",
      Hindi: "रिकॉर्डिंग हो रही है..."
    }
  };

  // Function to add a new message to the state
  const addMessage = (role, content, props = {}) => {
    const newMessage = {
      id: `${Date.now()}-${Math.random()}`,
      role,
      content,
      timestamp: new Date(),
      ...props
    };
    setMessages(prev => [...prev, newMessage]);
    return newMessage;
  };

  useEffect(() => {
    if (!hasInitialized.current && messages.length === 0) {
      addMessage('assistant', TEXT.welcome_message[language]);
      hasInitialized.current = true;
    }
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Check if response indicates need for image upload
  const checkForImageRequest = (responseText) => {
    const imageKeywords = [
      'upload', 'image', 'photo', 'picture', 'leaf',
      'अपलोड', 'तस्वीर', 'फोटो', 'पत्ती', 'छवि'
    ];

    const lowerResponse = responseText.toLowerCase();
    return imageKeywords.some(keyword => lowerResponse.includes(keyword));
  };

  const sendMessage = async (text = inputValue) => {
    if (!text.trim() || isLoading) return;

    addMessage('user', text, { image: imagePreview });

    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          transcript: text,
          language: language,
          thread_id: threadId
        })
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      if (data.success) {
        const botMessage = addMessage('assistant', data.response);

        // Check if the response is asking for an image
        if (checkForImageRequest(data.response)) {
          setWaitingForImage(true);
          setPendingImageQuery(text);
        } else {
          setWaitingForImage(false);
          setPendingImageQuery(null);
        }

        // --- Automatically play the response ---
        // handlePlayAudio(data.response, botMessage.id); // Uncomment this line to auto-play

      } else {
        throw new Error(data.error || 'Unknown error');
      }
    } catch (error) {
      console.error('Error:', error);
      addMessage('assistant', TEXT.error[language], { isError: true });
    } finally {
      setIsLoading(false);
      setSelectedImage(null);
      setImagePreview(null);
      setImageQueryInput('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleSuggestionClick = (suggestion) => {
    sendMessage(suggestion);
  };

  const handleImageSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);

      setWaitingForImage(true);
      setPendingImageQuery(null);
      setImageQueryInput('');
    }
  };

  const handleImageUpload = async () => {
    if (!selectedImage) return;

    setIsLoading(true);

    try {
      // Upload image to backend (saves to fixed path)
      const formData = new FormData();
      formData.append('file', selectedImage);

      const uploadResponse = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData
      });

      if (!uploadResponse.ok) {
        throw new Error('Image upload failed');
      }

      const uploadData = await uploadResponse.json();

      const queryText = imageQueryInput.trim() || pendingImageQuery || "Please analyze this plant image for diseases";

      // Send message - backend will use the fixed path
      await sendMessage(queryText);

      setWaitingForImage(false);
      setPendingImageQuery(null);
    } catch (error) {
      console.error('Upload error:', error);
      addMessage('assistant',
        language === 'English'
          ? "Sorry, I couldn't upload the image. Please try again."
          : "क्षमा करें, मैं तस्वीर अपलोड नहीं कर सका। कृपया पुनः प्रयास करें।",
        { isError: true }
      );
      setIsLoading(false);
    }
  };

  // --- NEW STT FUNCTIONS ---
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };

      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

        // Stop all audio tracks to release the mic
        stream.getTracks().forEach(track => track.stop());

        const formData = new FormData();
        formData.append('file', audioBlob, 'recording.webm');

        setIsLoading(true); // Use main loader
        try {
          const response = await fetch(`${API_BASE_URL}/stt`, {
            method: 'POST',
            body: formData,
          });

          if (!response.ok) throw new Error('STT request failed');

          const data = await response.json();
          if (data.success && data.transcript) {
            setInputValue(data.transcript); // Put transcript in input box
            // Optional: auto-send
            // sendMessage(data.transcript);
          } else {
            throw new Error(data.error || 'Failed to transcribe');
          }
        } catch (error) {
          console.error('STT Error:', error);
          addMessage('assistant', TEXT.stt_error[language], { isError: true });
        } finally {
          setIsLoading(false);
        }
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
      addMessage('assistant', 'Could not start recording. Please check microphone permissions.', { isError: true });
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    setIsRecording(false);
  };

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording();
    } else {
      startRecording();
    }
  };

  // --- NEW TTS FUNCTIONS ---
  const stopAudio = () => {
    if (audioPlayerRef.current) {
      audioPlayerRef.current.pause();
      audioPlayerRef.current = null;
    }
    setCurrentPlayingMessageId(null);
    setIsAudioLoading(false);
  };

  const handlePlayAudio = async (text, messageId) => {
    // If clicking the button of the currently playing audio, stop it.
    if (audioPlayerRef.current && currentPlayingMessageId === messageId) {
      stopAudio();
      return;
    }

    // If playing other audio, stop it first.
    if (audioPlayerRef.current) {
      stopAudio();
    }

    // Start playing new audio
    setCurrentPlayingMessageId(messageId);
    setIsAudioLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/tts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        throw new Error('TTS request failed');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      audioPlayerRef.current = new Audio(audioUrl);
      audioPlayerRef.current.play();

      audioPlayerRef.current.onended = () => {
        stopAudio();
      };

      audioPlayerRef.current.onerror = () => {
        console.error('Audio playback error');
        stopAudio();
        addMessage('assistant', TEXT.tts_error[language], { isError: true });
      };

    } catch (error) {
      console.error('TTS Error:', error);
      addMessage('assistant', TEXT.tts_error[language], { isError: true });
      stopAudio(); // Reset state on error
    } finally {
      setIsAudioLoading(false); // Loader is only for the fetch part
    }
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-emerald-50 via-teal-50 to-cyan-50">
      {/* Sidebar */}
      <div className={`${sidebarOpen ? 'w-80' : 'w-0'} transition-all duration-300 bg-white/90 backdrop-blur-sm shadow-2xl overflow-hidden`}>
        <div className="p-6 h-full flex flex-col">
          {/* Logo Section */}
          <div className="mb-6">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center shadow-lg">
                <Leaf className="text-white" size={28} />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                  {TEXT.sidebar_title[language]}
                </h1>
                <p className="text-xs text-gray-500">AI-Powered Farming Aid</p>
              </div>
            </div>
          </div>

          {/* Language Toggle */}
          <div className="mb-6">
            <div className="bg-gray-100 rounded-xl p-1 flex gap-1">
              <button
                onClick={() => setLanguage('English')}
                className={`flex-1 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all ${
                  language === 'English'
                    ? 'bg-white text-green-600 shadow-md'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage('Hindi')}
                className={`flex-1 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all ${
                  language === 'Hindi'
                    ? 'bg-white text-green-600 shadow-md'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                हिंदी
              </button>
            </div>
          </div>

          {/* Capabilities */}
          <div className="mb-6 flex-1 overflow-y-auto">
            <h3 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wide">
              {TEXT.capabilities[language]}
            </h3>
            <div className="space-y-2">
              {TEXT.features[language].map((feature, idx) => (
                <div key={idx} className="text-sm text-gray-600 py-2 px-3 bg-gray-50 rounded-lg">
                  {feature}
                </div>
              ))}
            </div>
          </div>

          {/* Session Info */}
          <div className="mt-auto pt-4 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              <p className="mb-1">Session: Active</p>
              <p className="font-mono truncate">{threadId.slice(0, 20)}...</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-md shadow-sm border-b border-gray-200">
          <div className="px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
              </button>
              <div className="flex items-center gap-2">
                <MessageSquare className="text-green-600" size={24} />
                <h2 className="text-xl font-semibold text-gray-800">Chat Assistant</h2>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-sm text-gray-600">Online</span>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-6">
          <div className="max-w-4xl mx-auto space-y-6">
            {/* Quick Suggestions (shown initially) */}
            {messages.length <= 1 && (
              <div className="mb-8">
                <h3 className="text-sm font-semibold text-gray-600 mb-4 text-center">
                  {TEXT.quick_questions[language]}
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {TEXT.suggestions[language].map((suggestion, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="p-4 bg-white rounded-xl shadow-sm hover:shadow-md transition-all text-left border-2 border-transparent hover:border-green-500 group"
                    >
                      <p className="text-sm text-gray-700 group-hover:text-green-700 font-medium">
                        {suggestion}
                      </p>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Messages */}
            {messages.map((msg) => (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                <div className={`max-w-2xl ${
                  msg.role === 'user'
                    ? 'bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-3xl rounded-br-sm'
                    : msg.isError
                      ? 'bg-red-50 border-2 border-red-200 text-red-800 rounded-3xl rounded-bl-sm'
                      : 'bg-white shadow-md rounded-3xl rounded-bl-sm border border-gray-100'
                } px-6 py-4`}>

                  {/* --- TTS Button for Assistant --- */}
                  {msg.role === 'assistant' && (
                    <div className="flex items-center justify-between gap-2 mb-2">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center">
                          <Leaf className="text-white" size={16} />
                        </div>
                        <span className="text-xs font-semibold text-gray-500">KrishiMitra</span>
                      </div>

                      {!msg.isError && (
                        <button
                          onClick={() => handlePlayAudio(msg.content, msg.id)}
                          disabled={isAudioLoading && currentPlayingMessageId === msg.id}
                          className="p-1 rounded-full text-gray-500 hover:bg-gray-100 hover:text-green-600 transition"
                        >
                          {isAudioLoading && currentPlayingMessageId === msg.id ? (
                            <Loader2 size={18} className="animate-spin" />
                          ) : currentPlayingMessageId === msg.id ? (
                            <Pause size={18} />
                          ) : (
                            <Play size={18} />
                          )}
                        </button>
                      )}
                    </div>
                  )}

                  {msg.image && (
                    <img src={msg.image} alt="Uploaded" className="rounded-lg mb-3 max-w-xs" />
                  )}
                  <div className={`whitespace-pre-wrap ${msg.role === 'user' ? 'text-white' : 'text-gray-800'}`}>
                    {msg.content}
                  </div>
                  <div className={`text-xs mt-2 ${msg.role === 'user' ? 'text-green-100' : 'text-gray-400'}`}>
                    {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}

            {/* Image Upload UI */}
            {waitingForImage && (
              <div className="animate-fadeIn">
                <div className="bg-white rounded-2xl shadow-lg border-2 border-green-200 p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <ImagePlus className="text-green-600" size={24} />
                    <h3 className="font-semibold text-gray-800">{TEXT.upload_prompt[language]}</h3>
                  </div>

                  {!selectedImage ? (
                    <button
                      onClick={() => fileInputRef.current?.click()}
                      className="w-full p-8 border-2 border-dashed border-gray-300 rounded-xl hover:border-green-500 transition-all group"
                    >
                      <Upload className="mx-auto mb-3 text-gray-400 group-hover:text-green-600" size={48} />
                      <p className="text-gray-600 group-hover:text-green-700 font-medium">
                        {TEXT.upload_button[language]}
                      </p>
                      <p className="text-xs text-gray-400 mt-2">JPG, PNG (Max 10MB)</p>
                    </button>
                  ) : (
                    <div className="space-y-4">
                      <div className="relative">
                        <img src={imagePreview} alt="Preview" className="w-full rounded-xl max-h-64 object-cover" />
                        <button
                          onClick={() => {
                            setSelectedImage(null);
                            setImagePreview(null);
                            setImageQueryInput('');
                          }}
                          className="absolute top-2 right-2 p-2 bg-red-500 text-white rounded-full hover:bg-red-600 transition"
                        >
                          <X size={16} />
                        </button>
                      </div>

                      <input
                        type="text"
                        value={imageQueryInput}
                        onChange={(e) => setImageQueryInput(e.target.value)}
                        placeholder={TEXT.image_query_placeholder[language]}
                        className="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-green-500 transition-all"
                      />

                      <button
                        onClick={handleImageUpload}
                        disabled={isLoading}
                        className="w-full py-3 bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-xl font-semibold hover:shadow-lg transition-all disabled:opacity-50"
                      >
                        {isLoading ? (
                          <span className="flex items-center justify-center gap-2">
                            <Loader2 className="animate-spin" size={20} />
                            {language === 'English' ? 'Analyzing...' : 'विश्लेषण हो रहा है...'}
                          </span>
                        ) : (
                          TEXT.analyze_button[language]
                        )}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Loading Indicator */}
            {isLoading && !waitingForImage && (
              <div className="flex justify-start animate-fadeIn">
                <div className="bg-white shadow-md rounded-3xl rounded-bl-sm border border-gray-100 px-6 py-4">
                  <div className="flex items-center gap-3">
                    <Loader2 className="animate-spin text-green-600" size={20} />
                    <span className="text-gray-600">{TEXT.thinking[language]}</span>
                  </div>
                </div>
              </div>
            )}

            {/* --- Recording Indicator --- */}
            {isRecording && (
              <div className="flex justify-center animate-fadeIn">
                <div className="bg-red-100 text-red-700 shadow-md rounded-full px-6 py-3 border border-red-200">
                  <div className="flex items-center gap-3">
                    <Mic className="animate-pulse text-red-600" size={20} />
                    <span className="font-medium">{TEXT.recording[language]}</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white/80 backdrop-blur-md border-t border-gray-200 px-6 py-4">

          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageSelect}
            className="hidden"
          />

          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3 items-end">

              <button
                onClick={() => fileInputRef.current?.click()}
                disabled={isLoading || waitingForImage || isRecording}
                className="p-4 bg-white rounded-2xl shadow-lg border-2 border-gray-200 hover:border-green-500 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Upload image"
              >
                <ImagePlus size={24} className="text-gray-500" />
              </button>

              <div className="flex-1 bg-white rounded-2xl shadow-lg border-2 border-gray-200 focus-within:border-green-500 transition-all">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={TEXT.chat_placeholder[language]}
                  disabled={isLoading || waitingForImage || isRecording}
                  rows={1}
                  className="w-full px-6 py-4 bg-transparent resize-none focus:outline-none text-gray-800 placeholder-gray-400"
                  style={{ minHeight: '56px', maxHeight: '120px' }}
                />
              </div>

              {/* --- STT Button --- */}
              <button
                onClick={toggleRecording}
                disabled={isLoading || waitingForImage}
                className={`p-4 rounded-2xl hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed
                  ${isRecording
                  ? 'bg-red-500 text-white'
                  : 'bg-white text-gray-600 shadow-lg border-2 border-gray-200 hover:border-blue-500'
                }`}
              >
                {isRecording ? <MicOff size={24} /> : <Mic size={24} />}
              </button>

              {/* --- Send Button --- */}
              <button
                onClick={() => sendMessage()}
                disabled={!inputValue.trim() || isLoading || waitingForImage || isRecording}
                className="p-4 bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-2xl hover:shadow-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg"
              >
                {isLoading ? (
                  <Loader2 className="animate-spin" size={24} />
                ) : (
                  <Send size={24} />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <style jsx>{`
          @keyframes fadeIn {
              from {
                  opacity: 0;
                  transform: translateY(10px);
              }
              to {
                  opacity: 1;
                  transform: translateY(0);
              }
          }
          .animate-fadeIn {
              animation: fadeIn 0.3s ease-out;
          }
      `}</style>
    </div>
  );
};

export default KrishiMitra;