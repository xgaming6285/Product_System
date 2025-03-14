document.addEventListener('DOMContentLoaded', () => {
            // DOM Elements
            const fileInput = document.getElementById('file-input');
            const fileList = document.getElementById('file-list');
            const uploadBtn = document.getElementById('upload-btn');
            const uploadStatus = document.getElementById('upload-status');
            const chatMessages = document.getElementById('chat-messages');
            const chatInput = document.getElementById('chat-input');
            const sendBtn = document.getElementById('send-btn');
            const chatStatus = document.getElementById('chat-status');
            const fileInputContainer = document.querySelector('.file-input-container');
            
            // Add initial welcome message
            addMessage('Hello! I am the Products Agent. Upload your product catalogs and I can answer questions about them.', 'agent');
            
            // Drag and drop effects
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                fileInputContainer.addEventListener(eventName, preventDefaults, false);
            });

            function preventDefaults(e) {
                e.preventDefault();
                e.stopPropagation();
            }

            ['dragenter', 'dragover'].forEach(eventName => {
                fileInputContainer.addEventListener(eventName, () => {
                    fileInputContainer.classList.add('drag-over');
                });
            });

            ['dragleave', 'drop'].forEach(eventName => {
                fileInputContainer.addEventListener(eventName, () => {
                    fileInputContainer.classList.remove('drag-over');
                });
            });

            // Handle file drop
            fileInputContainer.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                fileInput.files = files;
                displaySelectedFiles();
            });
            
            // Handle file selection
            fileInput.addEventListener('change', () => {
                displaySelectedFiles();
            });
            
            // Display selected files
            function displaySelectedFiles() {
                const files = fileInput.files;
                
                if (files.length > 0) {
                    fileList.classList.remove('hidden');
                    uploadBtn.disabled = false;
                    
                    fileList.innerHTML = '';
                    for (const file of files) {
                        const fileItem = document.createElement('div');
                        fileItem.className = 'file-item';
                        fileItem.innerHTML = `
                            <span>${file.name}</span>
                            <span>${formatFileSize(file.size)}</span>
                        `;
                        fileList.appendChild(fileItem);
                    }
                } else {
                    fileList.classList.add('hidden');
                    uploadBtn.disabled = true;
                }
            }
            
            // Format file size
            function formatFileSize(bytes) {
                if (bytes < 1024) return bytes + ' B';
                else if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
                else return (bytes / 1048576).toFixed(1) + ' MB';
            }
            
            // Handle file upload
            uploadBtn.addEventListener('click', async () => {
                if (fileInput.files.length === 0) return;
                
                const formData = new FormData();
                for (const file of fileInput.files) {
                    formData.append('files', file);
                }
                
                uploadBtn.disabled = true;
                uploadStatus.className = 'status loading';
                uploadStatus.textContent = 'Uploading and processing files';
                uploadStatus.classList.remove('hidden');
                
                try {
                    const response = await fetch('/upload', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        uploadStatus.className = 'status success';
                        uploadStatus.textContent = result.message;
                        
                        // Clear file input
                        fileInput.value = '';
                        fileList.classList.add('hidden');
                        
                        // Add a message to the chat
                        addMessage('I have processed your catalog files. You can now ask questions about your products.', 'agent');
                    } else {
                        throw new Error(result.detail || 'Failed to upload files');
                    }
                } catch (error) {
                    uploadStatus.className = 'status error';
                    uploadStatus.textContent = `Error: ${error.message}`;
                } finally {
                    uploadBtn.disabled = false;
                }
            });
            
            // Send chat message
            async function sendMessage() {
                const message = chatInput.value.trim();
                if (!message) return;
                
                // Add user message to chat
                addMessage(message, 'user');
                
                // Clear input
                chatInput.value = '';
                
                // Show loading indicator
                chatStatus.className = 'status loading';
                chatStatus.textContent = 'Getting response';
                chatStatus.classList.remove('hidden');
                
                const formData = new FormData();
                formData.append('question', message);
                
                try {
                    const response = await fetch('/chat', {
                        method: 'POST',
                        body: formData
                    });
                    
                    const result = await response.json();
                    
                    if (response.ok) {
                        addMessage(result.response, 'agent');
                        chatStatus.classList.add('hidden');
                    } else {
                        throw new Error(result.detail || 'Failed to get response');
                    }
                } catch (error) {
                    chatStatus.className = 'status error';
                    chatStatus.textContent = `Error: ${error.message}`;
                    setTimeout(() => {
                        chatStatus.classList.add('hidden');
                    }, 3000);
                }
            }
            
            // Add message to chat
            function addMessage(text, sender) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}-message`;
                messageDiv.textContent = text;
                
                chatMessages.appendChild(messageDiv);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
            
            // Send button click
            sendBtn.addEventListener('click', sendMessage);
            
            // Enter key press in input
            chatInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            // Button click effects
            document.querySelectorAll('button').forEach(button => {
                button.addEventListener('click', function(e) {
                    const rect = this.getBoundingClientRect();
                    const x = e.clientX - rect.left;
                    const y = e.clientY - rect.top;

                    const ripple = document.createElement('span');
                    ripple.style.cssText = `
                        position: absolute;
                        background: rgba(255, 255, 255, 0.7);
                        border-radius: 50%;
                        pointer-events: none;
                        width: 100px;
                        height: 100px;
                        left: ${x - 50}px;
                        top: ${y - 50}px;
                        transform: scale(0);
                        animation: ripple 0.6s linear;
                    `;

                    this.style.position = 'relative';
                    this.style.overflow = 'hidden';
                    this.appendChild(ripple);

                    setTimeout(() => ripple.remove(), 600);
                });
            });

            // Status message animations
            function showStatus(message, type = 'success') {
                const statusDiv = document.createElement('div');
                statusDiv.className = `status ${type}`;
                statusDiv.textContent = message;
                document.querySelector('.container').appendChild(statusDiv);
                setTimeout(() => {
                    statusDiv.remove();
                }, 3000);
            }
        });