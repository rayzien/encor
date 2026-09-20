// Safety Guardrails Page JS

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('safety-rules-form');
    const statusMsg = document.getElementById('safety-status-msg');
    const verifyBtn = document.getElementById('test-verify-btn');
    const resultsBox = document.getElementById('safety-test-results');

    // Fields
    const relEnabled = document.getElementById('safety-rel-enabled');
    const minFollowers = document.getElementById('safety-min-followers');
    const maxFollowers = document.getElementById('safety-max-followers');
    const minFollowing = document.getElementById('safety-min-following');
    const maxFollowing = document.getElementById('safety-max-following');
    const minPosts = document.getElementById('safety-min-posts');
    const maxPosts = document.getElementById('safety-max-posts');
    const potencyRatio = document.getElementById('safety-potency-ratio');

    const skipPrivate = document.getElementById('safety-skip-private');
    const skipNopic = document.getElementById('safety-skip-nopic');
    const skipVerified = document.getElementById('safety-skip-verified');
    const skipBusinessSelect = document.getElementById('safety-skip-business-select');
    const skipCategories = document.getElementById('safety-skip-categories');

    const ignoreWords = document.getElementById('safety-ignore-words');
    const mandatoryWords = document.getElementById('safety-mandatory-words');

    const ignoreUsers = document.getElementById('safety-ignore-users');
    const langSelect = document.getElementById('safety-language-select');

    async function loadSafetyRules() {
        try {
            const res = await fetch('/api/safety/rules');
            if (!res.ok) return;
            const data = await res.json();

            relEnabled.checked = data.relationship_bounds_enabled;
            minFollowers.value = data.min_followers;
            maxFollowers.value = data.max_followers;
            minFollowing.value = data.min_following;
            maxFollowing.value = data.max_following;
            minPosts.value = data.min_posts;
            maxPosts.value = data.max_posts;
            potencyRatio.value = data.potency_ratio;

            skipPrivate.checked = data.skip_private;
            skipNopic.checked = data.skip_no_profile_pic;
            skipVerified.checked = data.skip_verified;

            if (data.skip_business) skipBusinessSelect.value = 'business';
            else if (data.skip_non_business) skipBusinessSelect.value = 'non_business';
            else skipBusinessSelect.value = 'none';

            skipCategories.value = (data.skip_business_categories || []).join(', ');

            ignoreWords.value = (data.ignore_words || []).join(', ');
            mandatoryWords.value = (data.mandatory_words || []).join(', ');

            ignoreUsers.value = (data.ignore_users || []).join(', ');
            langSelect.value = (data.mandatory_language && data.mandatory_language[0]) || 'LATIN';
        } catch (err) {
            console.error('Error loading safety rules:', err);
        }
    }

    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();

            const skipBizVal = skipBusinessSelect.value;
            const categoriesList = skipCategories.value.split(',').map(s => s.trim()).filter(Boolean);
            const ignoreWordsList = ignoreWords.value.split(',').map(s => s.trim()).filter(Boolean);
            const mandatoryWordsList = mandatoryWords.value.split(',').map(s => s.trim()).filter(Boolean);
            const ignoreUsersList = ignoreUsers.value.split(',').map(s => s.trim()).filter(Boolean);

            const payload = {
                relationship_bounds_enabled: relEnabled.checked,
                min_followers: parseInt(minFollowers.value) || 0,
                max_followers: parseInt(maxFollowers.value) || 50000,
                min_following: parseInt(minFollowing.value) || 0,
                max_following: parseInt(maxFollowing.value) || 7500,
                min_posts: parseInt(minPosts.value) || 0,
                max_posts: parseInt(maxPosts.value) || 10000,
                potency_ratio: parseFloat(potencyRatio.value) || 0.0,

                skip_private: skipPrivate.checked,
                private_percentage: 100,
                skip_no_profile_pic: skipNopic.checked,
                no_profile_pic_percentage: 100,
                skip_business: skipBizVal === 'business',
                skip_non_business: skipBizVal === 'non_business',
                skip_business_categories: categoriesList,
                dont_skip_business_categories: [],
                skip_verified: skipVerified.checked,

                mandatory_words: mandatoryWordsList,
                ignore_words: ignoreWordsList,

                ignore_users: ignoreUsersList,
                mandatory_language: [langSelect.value]
            };

            try {
                const res = await fetch('/api/safety/rules', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });

                if (res.ok) {
                    statusMsg.style.display = 'inline';
                    setTimeout(() => statusMsg.style.display = 'none', 3000);
                }
            } catch (err) {
                console.error('Error saving safety rules:', err);
            }
        });
    }

    if (verifyBtn) {
        verifyBtn.addEventListener('click', async () => {
            const username = document.getElementById('test-username').value;
            const followers = parseInt(document.getElementById('test-followers').value) || 100;
            const following = parseInt(document.getElementById('test-following').value) || 100;

            try {
                const res = await fetch('/api/safety/verify-user', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: username,
                        followers: followers,
                        following: following,
                        posts: 10,
                        bio: 'Sample bio text for safety guardrail verification test'
                    })
                });

                if (res.ok) {
                    const data = await res.json();
                    resultsBox.style.display = 'block';
                    resultsBox.innerHTML = `Inspection Target: @${data.username}\nOverall Verdict: ${data.passed ? 'PASSED (APPROVED)' : 'SKIPPED (REJECTED)'}\nReason: ${data.reason}\n\nAudit Checklist Breakdown:\n` +
                        JSON.stringify(data.audit, null, 2);
                }
            } catch (err) {
                console.error('Error verifying user:', err);
            }
        });
    }

    loadSafetyRules();
});
