const subreddit = document.querySelector("#subreddit");
const analyzerButton = document.querySelector("#analyzer")
const results = document.querySelector("#Results");

function clickAnalyze(){
    analyzerButton.addEventListener("click", analyze);
}
clickAnalyze();

async function analyze(event){  // Add 'event' parameter
    event.preventDefault();  // ⭐ THIS IS THE KEY FIX - prevents form submission
    
    const userInput = subreddit.value.trim();
    if(userInput == "") {
        results.textContent = "Please enter a subreddit";
        return;
    }

    results.textContent = "Analyzing... (this may take 30-45 seconds)";
    
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 60000);

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ subredditStr: userInput }),
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || `Server error: ${response.status}`);
        }

        const data = await response.json();
        console.log('Success:', data);
        
        const score = parseFloat(data.score).toFixed(4);
        results.textContent = `Mental Health Score for r/${data.subreddit}: ${score}`;
        
    } catch (error) {
        clearTimeout(timeoutId);
        console.error('Error:', error);
        
        if (error.name === 'AbortError') {
            results.textContent = 'Request timed out. Reddit may be slow or subreddit has too many posts.';
        } else if (error.message.includes('Failed to fetch')) {
            results.textContent = 'Cannot connect to server. Make sure backend is running on port 8000.';
        } else {
            results.textContent = `Error: ${error.message}`;
        }
    }
}