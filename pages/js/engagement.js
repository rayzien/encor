// Engagement Rules JS

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('engagement-rules-form');
    const statusMsg = document.getElementById('rules-status-msg');
    const testSpintaxBtn = document.getElementById('test-spintax-btn');
    const spintaxPreview = document.getElementById('spintax-preview-results');

    // Fields
    const doLike = document.getElementById('rule-do-like');
    const likePct = document.getElementById('rule-like-percentage');
    const likeMin = document.getElementById('rule-like-min');
    const likeMax = document.getElementById('rule-like-max');

    const doComment = document.getElementById('rule-do-comment');
    const commentPct = document.getElementById('rule-comment-percentage');
    const commentMin = document.getElementById('rule-comment-min');
    const commentMax = document.getElementById('rule-comment-max');
    const commentsSpintax = document.getElementById('rule-comments-spintax');

    const doCommentLikes = document.getElementById('rule-do-comment-likes');
    const commentLikesPct = document.getElementById('rule-comment-likes-percentage');
    const commentLikesMax = document.getElementById('rule-comment-likes-max');

    const doFollow = document.getElementById('rule-do-follow');
    const followPct = document.getElementById('rule-follow-percentage');
    const interactAmount = document.getElementById('rule-user-interact-amount');
    const interactMedia = document.getElementById('rule-user-interact-media');

    const doStory = document.getElementById('rule-do-story');
    const storyPct = document.getElementById('rule-story-percentage');

    async function loadRules() {
        try {
            const res = await fetch('/api/engagement/rules');
            if (!res.ok) return;
            const data = await res.json();

            doLike.checked = data.do_like_enabled;
            likePct.value = data.do_like_percentage;
            likeMin.value = data.delimit_liking_min;
            likeMax.value = data.delimit_liking_max;

            doComment.checked = data.do_comment_enabled;
            commentPct.value = data.do_comment_percentage;
            commentMin.value = data.delimit_commenting_min;
            commentMax.value = data.delimit_commenting_max;
            commentsSpintax.value = (data.comments_spintax || []).join('\n');

            doCommentLikes.checked = data.do_comment_likes_enabled;
            commentLikesPct.value = data.do_comment_likes_percentage;
            commentLikesMax.value = data.comment_likes_max;

            doFollow.checked = data.do_follow_enabled;
            followPct.value = data.do_follow_percentage;
            interactAmount.value = data.user_interact_amount;
            interactMedia.value = data.user_interact_media || 'Photo';

            doStory.checked = data.do_story_enabled;
            storyPct.value = data.do_story_percentage;
        } catch (err) {
            console.error('Error loading engagement rules:', err);
        }
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const spintaxList = commentsSpintax.value.split('\n').map(s => s.trim()).filter(Boolean);

            const payload = {
                do_like_enabled: doLike.checked,
                do_like_percentage: parseInt(likePct.value) || 100,
                delimit_liking_min: parseInt(likeMin.value) || 0,
                delimit_liking_max: parseInt(likeMax.value) || 10000,

                do_comment_enabled: doComment.checked,
                do_comment_percentage: parseInt(commentPct.value) || 100,
                delimit_commenting_min: parseInt(commentMin.value) || 0,
                delimit_commenting_max: parseInt(commentMax.value) || 500,
                comments_spintax: spintaxList,

                do_comment_likes_enabled: doCommentLikes.checked,
                do_comment_likes_percentage: parseInt(commentLikesPct.value) || 50,
                comment_likes_max: parseInt(commentLikesMax.value) || 3,

                do_follow_enabled: doFollow.checked,
                do_follow_percentage: parseInt(followPct.value) || 100,

                user_interact_amount: parseInt(interactAmount.value) || 3,
                user_interact_percentage: 100,
                user_interact_randomize: true,
                user_interact_media: interactMedia.value,

                do_story_enabled: doStory.checked,
                do_story_percentage: parseInt(storyPct.value) || 100
            };

            try {
                const res = await fetch('/api/engagement/rules', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    statusMsg.style.display = 'inline';
                    setTimeout(() => statusMsg.style.display = 'none', 3000);
                }
            } catch (err) {
                console.error('Error saving engagement rules:', err);
            }
        });
    }

    if (testSpintaxBtn) {
        testSpintaxBtn.addEventListener('click', async () => {
            const raw = commentsSpintax.value.split('\n')[0] || '{Awesome|Great|Love this} {pic|shot|photo}!';
            try {
                const res = await fetch('/api/engagement/spintax/test', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ spintax: raw, sample_count: 5 })
                });

                if (res.ok) {
                    const data = await res.json();
                    spintaxPreview.style.display = 'block';
                    spintaxPreview.innerHTML = `Template: ${data.spintax}\nTotal Unique Variations: ${data.total_variations}\n\nSample Generated Outputs:\n` +
                        data.samples.map((s, i) => `[${i+1}] ${s}`).join('\n');
                }
            } catch (err) {
                console.error('Spintax test error:', err);
            }
        });
    }

    loadRules();
});
