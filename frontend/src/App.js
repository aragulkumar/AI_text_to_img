import { useState} from 'react';
import axios from 'axios';

function App() {

  const [prompt, setPrompt] = useState("");
  const [image, setImage] = useState(null);

  const handleGenerate = async () => {
    const res = await axios.post("http://127.0.0.1:8000/api/generate/",{prompt});
    setImage(res.data.url || res.data[0]?.generated_image);

  };

  return (
    <div>
      <h1> AI Image Generator</h1>
      <input
        type="text"
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        placeholder="Enter your prompt..."
      />
      <button onClick={handleGenerate}>Generate</button>
      {image && <img src={image} alt="AI Result"/>}
    
    </div>
  );
}

export default App;
