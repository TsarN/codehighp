(function() {
    function onVoteClick(kind, delta) {
        return function() {
            let parentEl = this.parentElement;
            let countEl = parentEl.querySelector('.vote-count');
            let count = parseInt(countEl.innerHTML);
            let url = '/blog/vote/' + this.dataset.post + '?action=';
            if (this.classList.contains('active')) {
                url += 'retract';
                this.classList.remove('active');
                count -= delta;
            } else {
                url += kind;
                let active = parentEl.querySelector('.active');
                if (active) {
                    active.classList.remove('active');
                    count += delta;
                }
                this.classList.add('active');
                count += delta;
            }

            if (count < 0) {
                countEl.classList.add('negative-vote-count');
            } else {
                countEl.classList.remove('negative-vote-count');
            }

            if (count > 0) {
                count = '+' + count.toString();
            } else {
                count = count.toString();
            }

            countEl.innerHTML = count;

            let request = new XMLHttpRequest();
            request.open("POST", url);
            request.setRequestHeader('X-CSRFToken', window.CSRF_TOKEN);
            request.send();
        }
    }

    let voteHandlers = {
        'upvote': onVoteClick('upvote', 1),
        'downvote': onVoteClick('downvote', -1)
    };

    function initVoteButtons(kind) {
        let els = document.getElementsByClassName(kind + "-button");
        for (let i = 0; i < els.length; ++i) {
            els[i].onclick = voteHandlers[kind];
        }
    }

    initVoteButtons("upvote");
    initVoteButtons("downvote");
})();