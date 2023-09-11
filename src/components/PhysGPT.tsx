import { Link } from "react-router-dom";

const PhysGPT = () => {
    console.log('Trying to hit GPT')
    return (
        // This page should validate the user and redirect if unauthenticated.
        <div>
            <section>
                <p>Congratulations, you have access to the Mock GPT application.</p>
                <Link to="/logout">Log out</Link>
            </section>
        </div>
    );
}

export default PhysGPT
