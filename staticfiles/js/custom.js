// Change Avatar
$(document).ready(function () {

    $('#upload-button').on('click', function () {
        $('#change-avatar').click();
    });


    $('#change-avatar').on('change', function (e) {
        const file = e.target.files[0];
        if (file) {
            const formData = new FormData();
            formData.append('avatar', file);
            const uploadUrl = document.querySelector('meta[name="avatar-upload-url"]').getAttribute('content');


            $.ajax({
                url: uploadUrl,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                success: function (response) {
                    if (response.success) {
                        $('#user-avatar').attr('src', response.new_avatar_url);
                        alert('Avatar has been updated Successfully! you can see the changes after reload the page.');
                    } else {
                        alert('Something went wrong!');
                    }
                },
                error: function () {
                    alert('Something went wrong!');
                }
            });
        }
    });
});

// Profile Edit
$(document).ready(function () {
    $('.edit-btn').on('click', function (e) {
        e.preventDefault();

        const mediaDiv = $(this).closest('.media');
        if (!mediaDiv.hasClass('open')) {
            const username = $('#user_name').val();
            const country = $('#country').val();
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
            const uploadUrl = document.querySelector('meta[name="update-profile-url"]').getAttribute('content');

            $.ajax({
                url: uploadUrl,
                type: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                data: {
                    username: username,
                    country: country,
                },
                success: function (response) {
                    alert('Profile has been updated successfully');
                    const newFlagUrl = response.new_flag_url;
                    $('#display_name').first().text(username);
                    $('#country_name').last().text(country);
                    $('#country_logo').attr('src', newFlagUrl);
                },
                error: function (xhr, status, error) {
                    alert('Something went wrong, please try again later!');
                }
            });

        }
    });
});

document.querySelectorAll('.emojis-sub-contain li').forEach(emoji => {
    emoji.addEventListener('click', function (event) {
        event.preventDefault();
        send_button.classList.remove('disabled');
        send_button.disabled = false;
    });
});

function toggleGalleryForm() {
    var form = document.getElementById("gallery-form");
    form.style.display = form.style.display === "none" ? "block" : "none";
}

function copyToClipboard(messageId) {
    const messageElement = "message-text-" + messageId;
    const text = document.getElementById(messageElement).innerText;

    navigator.clipboard.writeText(text)
        .then(() => {
            alert("message has been copied to clipboard.");
        })
        .catch(err => {
            console.error("can't do this right now!", err);
        });
}