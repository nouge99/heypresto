// I used ChatGPT to troubleshoot my javascript throughout this project – which
// incidentally was extremely helpful for clarifying for me how js syntax worked.

// I also occasionally used ChatGPT to suggest ways get certain effects I was after,
// which I've noted where applicable.

const popInForm = document.getElementById('hide-until-needed');
const popOutForm = document.getElementById('hide-after-push');
const boxInfo = document.getElementById('box-info');


function expandBoxes() {
    let expanders = document.querySelectorAll('.expander');
    let counter = 0;

    // Hide the button
    popOutForm.style.display = 'none';

    let currentHeight = boxInfo.clientHeight;
    let expandedHeight;

    let boxType = document.getElementById('box-type').getAttribute('data-type');
    console.log(boxType)
    if (boxType === 'image') {
        expandedHeight = currentHeight + 280;
    } else if ( boxType === 'number') {
        expandedHeight = currentHeight + 200;
    } else {
        expandedHeight = currentHeight + 260;
    }

    // * ChatGPT suggested * Count expander boxes and check they've finished
    function checkExpandEnd() {
        counter++;
        if (counter === expanders.length) {
            showForm()
        }
     }

    // * ChatGPT suggested * Add event listener to each expander box
    expanders.forEach(function(expander) {
        expander.addEventListener('transitionend', checkExpandEnd);
        expander.style.height = expandedHeight + 'px';
    });

    // Show the form
    function showForm() {
        popInForm.style.display = 'block';
    }
};


try {
    let fileInput = document.getElementById('file-upload');
    let boxType = document.getElementById('box-type').getAttribute('data-type');
    if (boxType === 'image') {
        fileInput.addEventListener('change', function(event) {

            let selectedFile = event.target.files[0];

            if (selectedFile.type !== 'image/jpeg' && selectedFile.type !== 'image/jpg' && selectedFile.type !== 'image/png' && selectedFile.type !== 'image/gif') {
                let uploadReport = document.getElementById('upload-report');
                uploadReport.innerHTML = '<span style="color: red; vertical-align: middle; font-size: 20px;">X</span>&nbsp;&nbsp;Image must be a jpg, gif or png';
            }
            else if (!selectedFile) {
                let uploadReport = document.getElementById('upload-report');
                uploadReport.innerHTML = '<span style="color: red; vertical-align: middle; font-size: 20px;">X</span>&nbsp;&nbsp;Choose an image to upload';
            }
            else if (selectedFile.size > (500 * 1000)) {
                let uploadReport = document.getElementById('upload-report');
                uploadReport.innerHTML = '<span style="color: red; vertical-align: middle; font-size: 20px;">X</span>&nbsp;&nbsp;Image must be smaller than 500kB';
            }
            else {
                let disabledButton = document.getElementById('disabled-until-ready');
                disabledButton.style.backgroundColor = '#3dd1e7';
                disabledButton.style.color = '#000000';
                disabledButton.removeAttribute('disabled');

                let uploadReport = document.getElementById('upload-report');
                uploadReport.innerHTML = '<span style="color: green; vertical-align: middle; font-size: 20px;">&#x2713;</span>&nbsp;&nbsp;Image is good to go &#8211; hit submit';
            }
        })
    };
} catch {
}


function checkSubmission(event) {
    let boxType = document.getElementById('box-type').getAttribute('data-type');
    // Check if name field is empty
    let name = document.getElementById('name').value;
    if (name === '') {
        document.getElementById('name-report').innerHTML = '<span style="color: red; vertical-align: middle; font-size: 20px;">X</span>&nbsp;&nbsp;Enter your name';
        return false;
    }
    document.getElementById('name-report').innerHTML = '';

    // Check if box is text type, check for content
    if (boxType === 'text') {
        let content = document.getElementById('text').value;
        if (content === '') {
            document.getElementById('text-report').innerHTML = '<span style="color: red; vertical-align: middle; font-size: 20px;">X</span>&nbsp;&nbsp;Enter your submission';
            return false;
        }
    }

    // Check if box is number type, check for content
    if (boxType === 'number') {
        let content = document.getElementById('number').value;
        if (content === '') {
            document.getElementById('num-report').innerHTML = '<span style="color: red; vertical-align: middle; font-size: 20px;">X</span>&nbsp;&nbsp;Enter your submission';
            return false;
        }
    }

    // Check if box is image type
    if (boxType === 'image') {
        const formElement = document.getElementById('hide-until-needed');
        const formData = new FormData(formElement);

        // * ChatGPT suggested how to force a form submit (since my js broke it) *
        fetch('/submit', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (response.ok) {
                console.log('Form submitted successfully!');
                // Session data was being lost, so needed to manually post to route
                let sessionCode = document.querySelector('#disabled-until-ready').value;
                console.log('Session code: ', sessionCode);
                let formData = new FormData()
                formData.append('session_code', sessionCode);
                // Hand session code to route via post form
                fetch('/gobox', {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (response.ok) {
                        console.log('Session code submitted successfully');
                        // Force page to reload to show new data
                        window.location.reload();
                    } else {
                        console.error('Failed to submit session code');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });

            } else {
                console.error('Error:', response.statusText);
            }
        })
        .catch(error => {
            console.error('Network error:', error)
        });
        return false;
    }

    // Allow form submission if all tests passed
    return true;
};

const formSubmit = document.getElementById('hide-until-needed');

try {
    formSubmit.addEventListener('submit', function(event) {
        event.preventDefault();

        // Validate form
        if (checkSubmission()) {
            // If validated submit the form
            this.submit();
        }
    });
} catch {
}


function checkMakeBox(event) {
    let report = document.getElementById('make-box-report')

    console.log("checkMakeBox started")
    // Check for name violations
    let name = document.getElementById('name').value;
    if (name === '') {
        report.innerHTML = '<span style="color: red; vertical-align: middle; font-size: 30px;">X</span>&nbsp;&nbsp;Enter a box name';
        return false;
    } else if (name.length > 46) {
        report.innerHTML = '<span style="color: red; vertical-align: middle; font-size: 30px;">X</span>&nbsp;&nbsp;Keep your name under 46 characters';
        return false;
    }
    report.innerHTML = '';
    console.log("Name check passed")

    // Check if type is selected
    let type = document.getElementById('type').value;
    if (type === '') {
        report.innerHTML = '<span style="color: red; vertical-align: middle; font-size: 30px;">X</span>&nbsp;&nbsp;Choose a box type';
        return false;
    }
    report.innerHTML = '';
    console.log("Type check passed")

    // Check if number of users is valid
    let users = document.getElementById('users').value;
    if (users < 1 || users > 9 || users === '') {
        report.innerHTML = '<span style="color: red; vertical-align: middle; font-size: 30px;">X</span>&nbsp;&nbsp;Include from 1 to 8 people';
        return false;
    }
    console.log("Users check passed")

    // Check instructions length
    let instructions = document.getElementById('instructions').value;
    if (instructions.length > 164) {
        report.innerHTML = "<span style='color: red; vertical-align: middle; font-size: 30px;'>X</span>&nbsp;&nbsp;Instructions can't be longer than 164 characters";
        return false;
    }
    console.log("Instructions check passed")

    // Allow form submission if all tests passed
    return true;
};

try {
    document.getElementById('make-box').addEventListener('submit', function(event) {
        event.preventDefault();

        // Validate form
        if (checkMakeBox()) {
            // If validated submit the form
            HTMLFormElement.prototype.submit.call(this);
        }
    });
} catch {
}




const copyButton = document.getElementById('copyButton')

// * Attapted from ChatGPT suggestion for implimenting a copy-to-clipboard function *
try {
copyButton.addEventListener('click', function() {
    // Text to copy to clipboard
    let textToCopy = document.getElementById('code-to-copy').textContent;

    // Create a temporary textarea element
    var textarea = document.createElement('textarea');
    textarea.value = textToCopy;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';

    // Append the textarea to the document body
    document.body.appendChild(textarea);

    // Select the text inside the textarea
    textarea.select();

    // Copy the selected text to the clipboard
    document.execCommand('copy');

    // Remove the temporary textarea
    document.body.removeChild(textarea);

    alert('Text copied to clipboard: ' + textToCopy);
});
} catch {
}


const openBox = document.getElementById('open-box')

try {
    openBox.addEventListener('click', function() {

        // Set question marks to vibrate before reveal
        let toHide = document.querySelectorAll('.hide-when-opened');
        toHide.forEach(function(element) {
            element.classList.add('vibrating');
        });

        // Pulse open box button
        openBox.classList.add('pulse');

        let boxType = document.getElementById('box-type').getAttribute('data-type');
        let toReveal;

        if (boxType === 'image') {
            toReveal = document.querySelectorAll('.image-reveal-when-opened');
        } else {
            toReveal = document.querySelectorAll('.text-reveal-when-opened');
        }

        // * ChatGPT suggested using setTimeout * Delay each reveal for MAXIMUM SUSPENSE
        setTimeout(function() {
            for (let i = 0; i < toReveal.length; i++) {
                setTimeout(function() {
                    if (i < toHide.length) {
                        toHide[i].remove();
                    }

                    if (i < toReveal.length) {
                        toReveal[i].removeAttribute('hidden');
                    }
                }, i * 1000);
            }
            openBox.setAttribute('hidden', '');
        }, 1000);
    });
} catch {
}

// This block here to resolve a problem with content 'jumping' after being rendered, after
// I used a javascript hack to fix my box sizing

document.addEventListener('DOMContentLoaded', function() {
    console.log("Confirm DOM content loaded")
    try {
        const currentHeight = boxInfo.offsetHeight;

        document.getElementById('box-background').style.height = currentHeight + 'px';
        document.getElementById('box-border').style.height = currentHeight + 'px';

        // Show boxes once height set set to stop jump effect
        document.getElementById('hide-until-loaded').classList.add('visible');

        // Reveal second half of page once first part renders, to avoid jump effect
        document.querySelector('.wait-for-load').style.display = 'block';
    } catch {
    }
});
