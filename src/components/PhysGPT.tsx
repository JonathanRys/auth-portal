const PhysGPT = () => {
    return (
        // This page should validate the user and redirect if unauthenticated.
        <div>
            <section className="gpt-reply">
                <p>Congratulations, you have exclusive access to the worlds most knowledgable physicist, what would you like to know?</p>
            </section>
            <section className="user-query">
                <p>Ask a question below.</p>
            </section>
            <div className="input-container">
                <label htmlFor="search">What would you like to know?</label>
                <textarea id="search" className="user-input"></textarea>
            </div>
        </div>
    );
}

export default PhysGPT
