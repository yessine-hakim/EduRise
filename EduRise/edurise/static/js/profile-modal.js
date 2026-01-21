// Profile Edit Modal Functionality
function initProfileModal() {
    console.log('Initializing profile modal...');
    
    const modal = document.getElementById('profileModal');
    const openBtn = document.getElementById('openProfileModal');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelModal');
    const form = document.getElementById('profileEditForm');
    const fileInput = document.getElementById('profileImageInput');
    const modalMessage = document.getElementById('modalMessage');

    console.log('Profile modal elements found:', {
        modal: !!modal,
        openBtn: !!openBtn,
        closeBtn: !!closeBtn,
        cancelBtn: !!cancelBtn,
        form: !!form,
        fileInput: !!fileInput,
        modalMessage: !!modalMessage
    });

    if (!modal || !form) {
        console.error('Critical modal elements not found', { modal, form });
        return false;
    }

    // Close modal function
    function closeModal() {
        console.log('Closing modal');
        modal.classList.remove('active');
        modal.style.display = 'none';
        document.body.style.overflow = '';
        if (modalMessage) {
            modalMessage.style.display = 'none';
            modalMessage.textContent = '';
        }
    }

    // Only attach event listeners if not already handled by inline onclick
    if (closeBtn && !closeBtn.getAttribute('onclick')) {
        closeBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal();
        });
    }

    if (cancelBtn && !cancelBtn.getAttribute('onclick')) {
        cancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            closeModal();
        });
    }

    // Close on overlay click
    if (modal) {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                closeModal();
            }
        });
    }

    // Close on ESC key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && modal && modal.classList.contains('active')) {
            closeModal();
        }
    });

    // Image preview and validation
    if (fileInput) {
        fileInput.addEventListener('change', function (e) {
            const file = e.target.files[0];
            if (file) {
                // Validate file type
                const validImageTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
                if (!validImageTypes.includes(file.type)) {
                    showMessage('Please select a valid image file (JPG, PNG, GIF, or WebP)', 'error');
                    fileInput.value = '';
                    return;
                }

                // Validate file size (5MB)
                const maxSize = 5 * 1024 * 1024; // 5MB
                if (file.size > maxSize) {
                    showMessage('Image size must be less than 5MB', 'error');
                    fileInput.value = '';
                    return;
                }

                // Preview the image
                const reader = new FileReader();
                reader.onload = function (e) {
                    let preview = document.getElementById('modalAvatarPreview');
                    const placeholder = document.getElementById('modalAvatarPlaceholder');

                    if (!preview) {
                        // Create img element if it doesn't exist
                        preview = document.createElement('img');
                        preview.id = 'modalAvatarPreview';
                        preview.className = 'modal-avatar';
                        preview.alt = 'Profile Preview';
                        preview.onerror = function () {
                            this.style.display = 'none';
                            if (placeholder) placeholder.style.display = 'flex';
                        };

                        const container = document.querySelector('.current-profile-image');
                        if (container) {
                            if (placeholder) {
                                placeholder.style.display = 'none';
                            }
                            container.appendChild(preview);
                        }
                    }

                    preview.src = e.target.result;
                    preview.style.display = 'block';
                    if (placeholder) {
                        placeholder.style.display = 'none';
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }

    // Show message helper
    function showMessage(message, type = 'info') {
        if (!modalMessage) return;
        modalMessage.className = `modal-message ${type}`;
        modalMessage.textContent = message;
        modalMessage.style.display = 'block';
    }

    // Form submission
    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            console.log('Form submitted');

            // Validate form fields
            const firstName = document.getElementById('firstName')?.value.trim();
            const lastName = document.getElementById('lastName')?.value.trim();
            const email = document.getElementById('email')?.value.trim();

            if (!firstName) {
                showMessage('First name is required', 'error');
                return;
            }

            if (!lastName) {
                showMessage('Last name is required', 'error');
                return;
            }

            if (!email) {
                showMessage('Email is required', 'error');
                return;
            }

            // Validate email format
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showMessage('Please enter a valid email address', 'error');
                return;
            }

            const formData = new FormData(form);
            const saveBtn = document.getElementById('saveProfile');

            if (!saveBtn) return;

            // Disable button and show loading
            saveBtn.disabled = true;
            const originalText = saveBtn.textContent;
            saveBtn.textContent = 'Saving...';
            if (modalMessage) modalMessage.style.display = 'none';

            // Send AJAX request
            const actionUrl = form.getAttribute('action') || '/users/profile/edit/';
            console.log('Submitting to:', actionUrl);

            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                },
                credentials: 'same-origin'
            })
                .then(response => {
                    console.log('Response status:', response.status);
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => {
                    console.log('Response data:', data);
                    if (data.success) {
                        // Show success message
                        showMessage(data.message || 'Profile updated successfully!', 'success');

                        // Update sidebar
                        if (data.user) {
                            updateSidebar(data.user);
                        }

                        // Close modal after short delay
                        setTimeout(() => {
                            closeModal();
                            // Reset form
                            form.reset();
                            if (fileInput) fileInput.value = '';
                            if (modalMessage) modalMessage.style.display = 'none';
                        }, 1500);
                    } else {
                        // Show error message
                        if (data.errors && typeof data.errors === 'object') {
                            const errorMessages = Object.values(data.errors)
                                .flat()
                                .join('; ');
                            showMessage(errorMessages, 'error');
                        } else {
                            showMessage(data.message || 'An error occurred. Please try again.', 'error');
                        }
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showMessage('An error occurred. Please check your connection and try again.', 'error');
                })
                .finally(() => {
                    // Re-enable button
                    saveBtn.disabled = false;
                    saveBtn.textContent = originalText;
                });
        });
    }

    // Update sidebar with new user data
    function updateSidebar(userData) {
        // Update name
        const nameElement = document.querySelector('.user-info h3');
        if (nameElement && userData.full_name) {
            nameElement.textContent = userData.full_name;
        }

        // Update avatar
        const sidebarAvatar = document.querySelector('.sidebar .profile-avatar');
        const sidebarPlaceholder = document.querySelector('.sidebar .profile-avatar-placeholder');

        if (userData.profile_image_url) {
            const cacheBustedUrl = userData.profile_image_url + (userData.profile_image_url.includes('?') ? '&v=' : '?v=') + Date.now();
            if (sidebarAvatar) {
                sidebarAvatar.src = cacheBustedUrl;
                sidebarAvatar.style.display = 'block';
                sidebarAvatar.onerror = function () {
                    this.style.display = 'none';
                    if (sidebarPlaceholder) {
                        sidebarPlaceholder.style.display = 'flex';
                    }
                };
                if (sidebarPlaceholder) {
                    sidebarPlaceholder.style.display = 'none';
                }
            } else if (sidebarPlaceholder) {
                // Replace placeholder with image
                const img = document.createElement('img');
                img.src = cacheBustedUrl;
                img.alt = userData.full_name || 'Profile';
                img.className = 'profile-avatar';
                img.onerror = function () {
                    this.style.display = 'none';
                    sidebarPlaceholder.style.display = 'flex';
                };
                sidebarPlaceholder.parentNode.insertBefore(img, sidebarPlaceholder);
                sidebarPlaceholder.style.display = 'none';
            }
        } else {
            // Update placeholder initials
            if (sidebarPlaceholder && userData.initials) {
                sidebarPlaceholder.textContent = userData.initials;
                sidebarPlaceholder.style.display = 'flex';
                if (sidebarAvatar) {
                    sidebarAvatar.style.display = 'none';
                }
            }
        }
    }

    console.log('Profile modal initialization complete');
    return true;
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProfileModal);
} else {
    // DOM is already loaded
    initProfileModal();
}
 
