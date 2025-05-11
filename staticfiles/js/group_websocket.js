// const person_id = {{ sender.id }};
const person_id = document.querySelector('meta[name="person-id"]').getAttribute('content');
const group_slug = document.querySelector('meta[name="group-slug"]').getAttribute('content');
const websocketUrl = document.querySelector('meta[name="websocket-url"]').getAttribute('content');
const chat_websocket = new WebSocket(websocketUrl);

const upload_file_button = document.getElementById('upload_file_button');
const file_upload = document.getElementById('file_upload');
const upload_image_button = document.getElementById('upload_image_button');
const image_upload = document.getElementById('image_upload');
const message_area = document.getElementById('group_message_area');
const text_area = document.getElementById('setemoj');
const send_button = document.getElementById('send_button');
const my_avatar = document.querySelector('meta[name="my-avatar"]').getAttribute('content');

function scrollToBottom() {
    const lastMessage = message_area.lastElementChild;
    if (lastMessage) {
        lastMessage.scrollIntoView({behavior: 'smooth'});
    } else {
        console.error("No messages to scroll in!");
    }
}

document.addEventListener('DOMContentLoaded', function () {
        scrollToBottom();
    });

upload_file_button.addEventListener('click', function (event) {
    event.preventDefault();
    file_upload.click();
});

file_upload.addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const base64File = e.target.result;
            chat_websocket.send(JSON.stringify({
                type: 'new_file',
                file: base64File,
                filename: file.name,
            }));

            const now = new Date();
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                hour12: true,
            };
            let formattedDate = now.toLocaleString('en-US', options);
            formattedDate = formattedDate.replace('AM', 'a.m.').replace('PM', 'p.m.');

            function truncateFileName(fileName, maxLength) {
                if (fileName.length > maxLength) {
                    return fileName.substring(0, maxLength) + '...';
                }
                return fileName;
            }

            const truncatedFileName = truncateFileName(file.name, 10);


            message_area.insertAdjacentHTML('beforeend', `<li class="replies">
                                <div class="media">
                                    <div class="profile mr-4 bg-size"
                                         style="background-image: url('${my_avatar}'); background-size: cover; background-position: center center; display: block;">
                                        <img class="bg-img" src="${my_avatar}" alt="Avatar"
                                             style="display: none;"></div>
                                    <div class="media-body">
                                        <div class="contact-name">
                                            <h5>Me</h5>
                                            <h6>${formattedDate}</h6>
                                            <ul class="msg-box">
                                                \t<li class="msg-setting-main">
                                                    <a href="${base64File}" download="${file.name}">
                                                    <button class="btn btn-success">
                                                    Download ${truncatedFileName}</button>
                                                    </a>
                                                    <div class="group-seen-status"></div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </li>`);
            scrollToBottom();
        };
        reader.readAsDataURL(file);
    }
});

upload_image_button.addEventListener('click', function (event) {
    event.preventDefault();
    image_upload.click()
});
image_upload.addEventListener('change', function (event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            const base64Image = e.target.result;
            chat_websocket.send(JSON.stringify({
                type: 'new_image',
                image: base64Image,
            }));

            const now = new Date();
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                hour12: true,
            };
            let formattedDate = now.toLocaleString('en-US', options);
            formattedDate = formattedDate.replace('AM', 'a.m.').replace('PM', 'p.m.');


            message_area.insertAdjacentHTML('beforeend', `<li class="replies">
                                <div class="media">
                                    <div class="profile mr-4 bg-size"
                                         style="background-image: url('${my_avatar}'); background-size: cover; background-position: center center; display: block;">
                                        <img class="bg-img" src="${my_avatar}" alt="Avatar"
                                             style="display: none;"></div>
                                    <div class="media-body">
                                        <div class="contact-name">
                                            <h5>Me</h5>
                                            <h6></h6>
                                            <h6>${formattedDate}</h6>
                                            <ul class="msg-box">
                                                \t<li class="msg-setting-main">
                                                    <a href="${base64Image}" data-lightbox="image-${base64Image}">
                                                     <img src="${base64Image}"
                                                     style="max-width: 100%;">
                                                     </a>
                                                     <div class="group-seen-status"></div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </li>`);
            scrollToBottom();
        };
        reader.readAsDataURL(file);
    }
});

text_area.addEventListener('input', function () {
    if (text_area.value.trim() === "") {
        send_button.classList.add('disabled');
        send_button.disabled = true;
    } else {
        send_button.classList.remove('disabled');
        send_button.disabled = false;
    }
});

text_area.addEventListener('keydown', function (event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        if (!send_button.disabled) {
            send_button.click();
        }
    }
});


send_button.addEventListener('click', function () {
    let message = text_area.value.trim();
    console.log(message)
    if (message) {
        chat_websocket.send(`{"type":"new_message","message":"${message}"}`);
        const now = new Date();
        const options = {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            hour12: true,
        };
        let formattedDate = now.toLocaleString('en-US', options);
        formattedDate = formattedDate.replace('AM', 'a.m.').replace('PM', 'p.m.');

        const messageId = new Date().getTime();

        message_area.insertAdjacentHTML('beforeend', `<li class="replies">
                                <div class="media">
                                    <div class="profile mr-4 bg-size"
                                         style="background-image: url('${my_avatar}'); background-size: cover; background-position: center center; display: block;">
                                        <img class="bg-img" src="${my_avatar}" alt="Avatar"
                                             style="display: none;"></div>
                                    <div class="media-body">
                                        <div class="contact-name">
                                            <h5>Me</h5>
                                            <h6>${formattedDate}</h6>
                                            <ul class="msg-box">
                                                \t<li class="msg-setting-main">
                                                    <h5 id="message-text-${messageId}" class="rtl">${message}</h5>
                                                    <div class="group-seen-status"></div>
                                                    <div class="msg-dropdown-main">
                                                                    <div class="msg-setting"><i class="ti-more-alt"></i>
                                                                    </div>
                                                                    <div class="msg-dropdown">
                                                                        <ul>
                                                                            <li>
                                                                                <button style="background: none;border: none;font: inherit;color:#595959;width:100%;display: flex; align-items: center;cursor: pointer" onclick="copyToClipboard(${messageId})"><i style="font-size:16px;margin-right:8px"
                                                                                           class="ti-clipboard"></i>copy
                                                                                </button>
                                                                            </li>
                                                                        </ul>
                                                                    </div>
                                                                </div>
                                                </li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            </li>`);
        text_area.value = "";
        send_button.classList.add('disabled');
        send_button.disabled = true;

        scrollToBottom()
        $(message_area).on('click', '.msg-setting', function() {
                $(this).siblings('.msg-dropdown').toggle();
            });
    }
});

chat_websocket.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.type_of_data === 'new_message' || data.type_of_data === 'new_image' || data.type_of_data === 'new_file') {
        if (data.sender_id != person_id && data.group_slug == group_slug) {
            let messageHTML = `
            <li class="sent">
                <div class="media">
                    <div class="profile mr-4 bg-size" style="background-image: url('${data.avatar}'); background-size: cover; background-position: center center; display: block;">
                        <img class="bg-img" src="${data.avatar}" alt="Avatar" style="display: none;">
                    </div>
                    <div class="media-body">
                        <div class="contact-name">
                            <h5>${data.sender}</h5>
                            <h6>${data.date}</h6>
                            <ul class="msg-box">
                                <li class="msg-setting-main">
                                    ${data.type_of_data === 'new_message' ? `<h5 id="message-text-${data.id}" class="rtl">${data.data}</h5>` : ''}
                                    ${data.type_of_data === 'new_image' ? `<a href="${data.data}" data-lightbox="image-${data.id}"><img src="${data.data}" style="max-width: 100%;"></a>` : ''}
                                    ${data.type_of_data === 'new_file' ? `<a href="${data.data}" download="${data.filename}"><button class="btn btn-primary">Download ${data.filename}</button></a>` : ''}
                                    <div class="msg-dropdown-main">
                                                                    <div class="msg-setting"><i class="ti-more-alt"></i>
                                                                    </div>
                                                                    <div class="msg-dropdown">
                                                                        <ul>
                                                                            <li>
                                                                                <button style="background: none;border: none;font: inherit;color:#595959;width:100%;display: flex; align-items: center;cursor: pointer" onclick="copyToClipboard(${data.id})"><i style="font-size:16px;margin-right:8px"
                                                                                           class="ti-clipboard"></i>copy
                                                                                </button>
                                                                            </li>
                                                                        </ul>
                                                                    </div>
                                                                </div>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </li>`;

            message_area.insertAdjacentHTML('beforeend', messageHTML);
            scrollToBottom();
            $(message_area).on('click', '.msg-setting', function() {
                $(this).siblings('.msg-dropdown').toggle();
            });

            chat_websocket.send(`{"type":"i_have_seen_the_message"}`);
            chat_websocket.send(`{"type":"sidebar_update"}`);
        }
    } else if (data.type_of_data === "the_messages_have_been_seen_by_the_other") {
            const my_messages = document.getElementsByClassName('group-seen-status');
            for (let i = 0; my_messages.length > i; i++) {
                my_messages[i].classList.add('badge');
                my_messages[i].classList.add('badge-success');
                my_messages[i].classList.add('sm');
                my_messages[i].classList.add('ml-2');
                my_messages[i].textContent = 'R';
        }
    } else if (data.type_of_data === "sidebar_updated") {
        updateSidebar(data.conversation);
    }
};

function updateSidebar(data) {
    let sidebar = document.querySelector('.group-main');
    let existingItem = sidebar.querySelector(`li[data-to="${data.group_slug}"]`);

    if (existingItem) {
        existingItem.querySelector('#side_sender').innerHTML =`${data.sender}:&nbsp`;
        existingItem.querySelector('#side_group_msg').innerText = data.last_message;

        sidebar.prepend(existingItem);
    } else {
        let newItem = document.createElement('li');
        newItem.setAttribute('data-to', data.group_slug);
        newItem.innerHTML = `
            <div class="group-box">
                                     <a href="/group-chat/${data.group_slug}">      
                                                        <div class="profile bg-size"
                                                         style="background-image: url('${data.group_avatar}'); background-size: cover; background-position: center center; display: block;">
                                                        <img class="bg-img" src="${data.group_avatar}"
                                                             alt="Avatar" style="display: none;">
                                                    </div>
                                                    <div class="details">
                                                        <h5>${data.group_name}</h5>
                                                        <h6 id="side_sender" style="display: inline-block;">${data.sender}: &nbsp;</h6><h6 id="side_group_msg" style="display: inline-block;">${data.last_message}</h6>
                                                    </div>
                                                    </a>
                                                </div>
        `;
        sidebar.prepend(newItem);
    }
}

$(document).ready(function () {
    const scrollToBottomBtn = document.getElementById('scroll-to-bottom-btn');
    const message_area = document.getElementById('group_message_area');


    if (!scrollToBottomBtn || !message_area) {
        console.error("Something went wrong!");
        return;
    }

    function scrollToBottom() {
        const lastMessage = message_area.lastElementChild;
        if (lastMessage) {
            lastMessage.scrollIntoView({behavior: 'smooth'});
        } else {
            console.error("No messages to scroll in!");
        }
    }

    scrollToBottomBtn.addEventListener('click', function () {
        scrollToBottom();
    });
});