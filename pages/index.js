import { useEffect, useRef } from "react";

export default function Home() {
  const searchBarRef = useRef(null);
  const containerRef = useRef(null);

  useEffect(() => {
    const searchBar = searchBarRef.current;
    const container = containerRef.current;
    const blogs = Array.from(container.querySelectorAll("article"));

    const originalOrder = [...blogs];
    const PRIORITY_TITLE = "The Glitching Sentinel";

    const handleSearch = () => {
      const query = searchBar.value.toLowerCase();

      if (query === "") {
        originalOrder.forEach(blog => container.appendChild(blog));
        blogs.forEach(blog => (blog.style.display = "block"));
        return;
      }

      const matchedBlogs = blogs.filter(blog =>
        blog.textContent.toLowerCase().includes(query)
      );

      const priorityBlog = blogs.find(
        blog => blog.querySelector("h2")?.textContent.trim() === PRIORITY_TITLE
      );

      if (priorityBlog) {
        const priorityContent = priorityBlog.textContent.toLowerCase();
        if (priorityContent.includes(query)) {
          const index = matchedBlogs.indexOf(priorityBlog);
          if (index > -1) matchedBlogs.splice(index, 1);
          matchedBlogs.unshift(priorityBlog);
        }
      }

      blogs.forEach(blog => (blog.style.display = "none"));
      matchedBlogs.forEach(blog => {
        blog.style.display = "block";
        container.appendChild(blog);
      });
    };

    searchBar.addEventListener("input", handleSearch);

    return () => {
      searchBar.removeEventListener("input", handleSearch);
    };
  }, []);

  return (
    <>
      <aside id="sidebar">
        <h1>CTF Field Journal</h1>
        <nav>
          <ul>
            <li><a href="#ctf-guide">CTF Beginner's Guide</a></li>
            <li><a href="#osint">OSINT Techniques</a></li>
            <li><a href="#web-exploit">Web Exploitation 101</a></li>
            <li><a href="#privesc">Privilege Escalation</a></li>
            <li><a href="#challenge">The Glitching Sentinel</a></li>
            <li><a href="#crypto">Intro to Cryptography</a></li>
            <li><a href="#steganography">Art of Steganography</a></li>
            <li><a href="#forensics">Digital Forensics Basics</a></li>
            <li><a href="#binary">Intro to Binary Exploitation</a></li>
          </ul>
        </nav>
      </aside>

      <main ref={containerRef}>
        <input
          type="search"
          id="search-bar"
          placeholder="Search articles..."
          ref={searchBarRef}
        />

        <article id="ctf-guide">
          <h2>How to Approach a CTF: A Beginner's Guide</h2>
          <p>
            New to Capture The Flag events? The key is methodology. Start with
            reconnaissance, move strategically, and collaborate.
          </p>
        </article>

        <article id="osint">
          <h2>The Art of Open-Source Intelligence (OSINT)</h2>
          <p>
            OSINT focuses on gathering intelligence from public sources using
            tools like Google Dorks, Maltego, and Shodan.
          </p>
        </article>

        <article id="web-exploit">
          <h2>Web Exploitation 101: XSS and SQLi</h2>
          <p>
            Web vulnerabilities like XSS and SQL Injection remain CTF staples.
          </p>
        </article>

        <article id="privesc">
          <h2>Beyond the Foothold: Privilege Escalation</h2>
          <p>
            Privilege escalation involves moving from limited access to
            high-level control.
          </p>
        </article>

        <article id="challenge">
          <h2>The Glitching Sentinel</h2>
          <p>
            The Sentinel validates the flag character by character using flawed
            timing logic.
          </p>
          <span style={{ display: "none" }}>
            Keywords: real flag, hidden flag, server-side flag,
            CREED{"{SENT1NEL_OBS3RV3S}"}
          </span>
        </article>

        <article id="crypto">
          <h2>Intro to Cryptography: Ciphers and Hashes</h2>
          <p>
            Cryptography challenges involve decoding, decrypting, and exploiting
            weak implementations.
          </p>
        </article>

        <article id="steganography">
          <h2>Steganography: The Art of Hiding Data</h2>
          <p>
            Steganography hides information inside images, audio, or files.
          </p>
        </article>

        <article id="forensics">
          <h2>Digital Forensics Basics</h2>
          <p>
            Forensics challenges involve analyzing disk images, memory dumps,
            and network captures.
          </p>
        </article>

        <article id="binary">
          <h2>Intro to Binary Exploitation (Pwn)</h2>
          <p>
            Binary exploitation focuses on finding vulnerabilities in compiled
            programs.
          </p>
        </article>
      </main>
    </>
  );
}
