(function() {
    function clearAllForms() {
        let forms = document.querySelectorAll(".comment-form");
        for (let i = 0; i < forms.length; ++i) {
            forms[i].innerHTML = "";
            forms[i].style.display = "none";
        }
    }

    function spawnCommentForm(el, parent_id, comment_id) {
        if (el.style.display === "block") {
            clearAllForms();
            return;
        }
        clearAllForms();
        let form = document.getElementById('base-comment-form');
        el.innerHTML = form.innerHTML;
        el.querySelector('input[name="parent_id"]').value = parent_id;
        if (comment_id) {
            el.querySelector('input[name="comment_id"]').value = comment_id;
            el.querySelector('textarea[name="text"]').innerHTML =
                document.getElementById('original-markdown-' + comment_id).innerText;
        }
        el.style.display = "block";
    }

    function initReplyLinks() {
        let links = document.querySelectorAll(".comment-reply-link");
        for (let i = 0; i < links.length; ++i) {
            let comment_id = parseInt(links[i].dataset.comment);
            let form = document.getElementById("comment-form-" + comment_id);
            links[i].onclick = function() {
                spawnCommentForm(form, comment_id, null);
                return false;
            }
        }
    }

    function initEditLinks() {
        let links = document.querySelectorAll(".comment-edit-link");
        for (let i = 0; i < links.length; ++i) {
            let parent_id = parseInt(links[i].dataset.parent);
            let comment_id = parseInt(links[i].dataset.comment);
            let form = document.getElementById("comment-form-" + comment_id);
            links[i].onclick = function() {
                spawnCommentForm(form, parent_id, comment_id);
                return false;
            }
        }
    }

    function initNewCommentLink() {
        let link = document.getElementById("new-comment-link");
        if (!link) return;
        link.onclick = function() {
            let form = document.getElementById("new-comment-form");
            spawnCommentForm(form, parseInt(link.dataset.post), null);
            return false;
        }
    }

    initReplyLinks();
    initEditLinks();
    initNewCommentLink();
})();