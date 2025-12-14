document.addEventListener("DOMContentLoaded", () => {
    const searchBar = document.getElementById("search-bar");
    const container = document.querySelector("main");
    const blogs = Array.from(document.querySelectorAll("article"));

    // Store the original order of blogs
    const originalOrder = [...blogs];

    const PRIORITY_TITLE = "The Glitching Sentinel";

    const handleSearch = () => {
        const query = searchBar.value.toLowerCase();

        if (query === "") {
            // Restore original order
            originalOrder.forEach(blog => container.appendChild(blog));
            blogs.forEach(blog => blog.style.display = "block");
            return;
        }

        const matchedBlogs = blogs.filter(blog => {
            const fullContent = blog.textContent.toLowerCase();
            return fullContent.includes(query);
        });

        const priorityBlog = blogs.find(blog =>
            blog.querySelector("h2")?.textContent.trim() === PRIORITY_TITLE
        );

        if (priorityBlog) {
            const priorityContent = priorityBlog.textContent.toLowerCase();
            const contentMatch = priorityContent.includes(query);

            if (contentMatch) {
                const index = matchedBlogs.indexOf(priorityBlog);
                if (index > -1) {
                    matchedBlogs.splice(index, 1);
                }
                matchedBlogs.unshift(priorityBlog);
            }
        }

        // Render
        blogs.forEach(b => (b.style.display = "none"));
        matchedBlogs.forEach(blog => {
            blog.style.display = "block";
            container.appendChild(blog);
        });
    };

    searchBar.addEventListener("input", handleSearch);
});
