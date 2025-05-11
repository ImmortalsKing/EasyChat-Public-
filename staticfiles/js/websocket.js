const person_id = document.querySelector('meta[name="person-id"]').getAttribute('content');
// const person_id = {{ person.id }};
// const url = `ws://localhost:8000/websocket/${person_id}`;
const websocketUrl = document.querySelector('meta[name="websocket-url"]').getAttribute('content');
const chat_websocket = new WebSocket(websocketUrl);

const upload_file_button = document.getElementById('upload_file_button');
const file_upload = document.getElementById('file_upload');
const upload_image_button = document.getElementById('upload_image_button');
const image_upload = document.getElementById('image_upload');
const message_area = document.getElementById('message_area');
const text_area = document.getElementById('setemoj');
const send_button = document.getElementById('send_button');
// const my_avatar = '{{ me.avatar.url }}';
const my_avatar = document.querySelector('meta[name="my-avatar"]').getAttribute('content');
const is_superuser = document.querySelector('meta[name="is_superuser"]').getAttribute('content') === "True";

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


            message_area.insertAdjacentHTML('beforeend', `
                <li class="replies">
                    <div class="media">
                        <div class="profile mr-4 bg-size" style="background-image: url('${my_avatar}'); background-size: cover; background-position: center center;">
                            <img class="bg-img" src="${my_avatar}" alt="Avatar" style="display: none;">
                        </div>
                        <div class="media-body">
                            <div class="contact-name">
                                <h5>Me</h5>
                                <h6>${formattedDate}</h6>
                                <ul class="msg-box">
                                    <li class="msg-setting-main">
                                        <a href="${base64File}" download="${file.name}">
                                        <button class="btn btn-success">
                                        Download ${truncatedFileName}</button>
                                        </a>
                                        <div class="seen-status"></div>
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


            message_area.insertAdjacentHTML('beforeend', `
                <li class="replies">
                    <div class="media">
                        <div class="profile mr-4 bg-size"
                             style="background-image: url('${my_avatar}'); background-size: cover; background-position: center center; display: block;">
                            <img class="bg-img" src="${my_avatar}" alt="Avatar" style="display: none;">
                        </div>
                        <div class="media-body">
                            <div class="contact-name">
                                <h5>Me</h5>
                                <h6></h6>
                                <h6>${formattedDate}</h6>
                                <ul class="msg-box">
                                    <li class="msg-setting-main">
                                         <a href="${base64Image}" data-lightbox="image-${base64Image}">
                                                                <img src="${base64Image}"
                                                                        style="max-width: 100%;">
                                                                </a>
                                        <div class="seen-status"></div>
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
                                    <h6></h6>
                                    <h6>${formattedDate}</h6>
                                    <ul class="msg-box">
                                        <li class="msg-setting-main">
                                            <h5 id="message-text-${messageId}" class="rtl">${message}</h5>
                                            <div class="seen-status"></div>
                                            <div class="msg-dropdown-main">
                                                                    <div class="msg-setting"><i class="ti-more-alt"></i>
                                                                    </div>
                                                                    <div class="msg-dropdown">
                                                                        <ul>
                                                                            <li>
                                                                                <button style="background: none;border: none;font: inherit;color:#595959;width:100%;display: flex; align-items: center;cursor: pointer" onclick="copyToClipboard(${messageId})"><i style="font-size:16px;margin-right:8px"
                                                                                           class="ti-clipboard"></i>Copy
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


chat_websocket.onmessage = function (event) {
    const received_data = JSON.parse(event.data);

    if (received_data.type_of_data == 'new_message') {
        if (received_data.sender_id == person_id || received_data.receiver_id == person_id) {
            message_area.insertAdjacentHTML('beforeend', `<li class="sent">
                        <div class="media">
                            <div class="profile mr-4 bg-size"
                                 style="background-image: url('${received_data.avatar}'); background-size: cover; background-position: center center; display: block;">
                                <img class="bg-img" src="${received_data.avatar}" alt="Avatar"
                                     style="display: none;"></div>
                            <div class="media-body">
                                <div class="contact-name">
                                    <h5>${received_data.from}</h5>
                                    <h6>${received_data.date}</h6>
                                    <ul class="msg-box">
                                        <li class="msg-setting-main">
                                            <h5 id="message-text-${received_data.id}" class="rtl">${received_data.data}</h5>
                                            <div class="msg-dropdown-main">
                                                                    <div class="msg-setting"><i class="ti-more-alt"></i>
                                                                    </div>
                                                                    <div class="msg-dropdown">
                                                                        <ul>
                                                                            <li>
                                                                                <button style="background: none;border: none;font: inherit;color:#595959;width:100%;display: flex; align-items: center;cursor: pointer" onclick="copyToClipboard(${received_data.id})"><i style="font-size:16px;margin-right:8px"
                                                                                           class="ti-clipboard"></i>Copy
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
            $(message_area).on('click', '.msg-setting', function() {
                $(this).siblings('.msg-dropdown').toggle();
            });
            scrollToBottom()
            chat_websocket.send(`{"type":"i_have_seen_the_message"}`)
            chat_websocket.send(`{"type":"sidebar_update"}`)
        }
    } else if (received_data.type_of_data == 'new_image') {
        if (received_data.sender_id == person_id || received_data.receiver_id == person_id) {
            message_area.insertAdjacentHTML('beforeend', `<li class="sent">
            <div class="media">
                <div class="profile mr-4 bg-size"
                     style="background-image: url('${received_data.avatar}'); background-size: cover; background-position: center center; display: block;">
                    <img class="bg-img" src="${received_data.avatar}" alt="Avatar"
                         style="display: none;"></div>
                <div class="media-body">
                    <div class="contact-name">
                        <h5>${received_data.from}</h5>
                        <h6>${received_data.date}</h6>
                        <ul class="msg-box">
                            <li class="msg-setting-main">
                                <a href="${received_data.data}" data-lightbox="image-${received_data.id}">
                                                                <img src="${received_data.data}"
                                                                        style="max-width: 100%;">
                                                                </a>
                                
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        </li>`);
            scrollToBottom();
            chat_websocket.send(`{"type":"i_have_seen_the_message"}`);
            chat_websocket.send(`{"type":"sidebar_update"}`);
        }
    } else if (received_data.type_of_data == 'new_file') {
        if (received_data.sender_id == person_id || received_data.receiver_id == person_id) {
            message_area.insertAdjacentHTML('beforeend', `<li class="sent">
        <div class="media">
            <div class="profile mr-4 bg-size" style="background-image: url('${received_data.avatar}'); background-size: cover; background-position: center center;">
                <img class="bg-img" src="${received_data.avatar}" alt="Avatar" style="display: none;">
            </div>
            <div class="media-body">
                <div class="contact-name">
                    <h5>${received_data.from}</h5>
                    <h6>${received_data.date}</h6>
                    <ul class="msg-box">
                        <li class="msg-setting-main">
                            <a href="${received_data.data}" download="${received_data.filename}">
                            <button class="btn btn-primary">
                             Download ${received_data.filename}</button>
                             </a>
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    </li>`);
            scrollToBottom();
            chat_websocket.send(`{"type":"i_have_seen_the_message"}`);
            chat_websocket.send(`{"type":"sidebar_update"}`);
        }
    } else if (received_data.type_of_data == "the_messages_have_been_seen_by_the_other") {
        const my_messages = document.getElementsByClassName('seen-status');
        for (let i = 0; my_messages.length > i; i++) {
            my_messages[i].classList.add('badge');
            my_messages[i].classList.add('badge-success');
            my_messages[i].classList.add('sm');
            my_messages[i].classList.add('ml-2');
            my_messages[i].textContent = 'R';
        }
    } else if (received_data.type_of_data === "sidebar_updated") {
        updateSidebar(received_data.conversation);
    }
};

function updateSidebar(data) {
    let sidebar = document.querySelector('.chat-main');
    let existingItem = sidebar.querySelector(`li[data-to="${data.contact_id}"]`);

    if (existingItem) {
        existingItem.querySelector('.details h6').innerText = data.last_message;
        existingItem.querySelector('.date-status h6').innerText = data.last_date;

        sidebar.prepend(existingItem);
    } else {
        let newItem = document.createElement('li');
        newItem.setAttribute('data-to', data.contact_id);
        newItem.innerHTML = `
            <div class="chat-box">
                <a href="/chat/${data.contact_id}">
                    <div class="profile bg-size" style="background-image: url('${data.contact_avatar}'); background-size: cover; background-position: center center; display: block;"><img class="bg-img"
                                                                 src="${data.contact_avatar}"
                                                                 alt="Avatar" style="display: none;"></div>
                    <div class="details">
                        <h5>${data.contact_name}</h5>
                        <h6>${data.last_message}</h6>
                    </div>
                    <div class="date-status">
                        <h6>${data.last_date}</h6>
                    </div>
                </a>
            </div>
        `;
        sidebar.prepend(newItem);
    }
}

$(document).ready(function () {
    const scrollToBottomBtn = document.getElementById('scroll-to-bottom-btn');
    const message_area = document.getElementById('message_area');


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
