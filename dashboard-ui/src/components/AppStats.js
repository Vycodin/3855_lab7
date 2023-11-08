import React, { useEffect, useState } from 'react'
import '../App.css';

export default function AppStats() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://ky-3855.westus3.cloudapp.azure.com:8100/stats`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Received Stats")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Latest Stats</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Conflicts</th>
							<th>Operations</th>
						</tr>
						<tr>
							<td># Conflict: {stats['num_conflicts']}</td>
							<td># Operations: {stats['num_operations']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Blufor: {stats['max_blu']}</td>
						</tr>
						<tr>
							<td colspan="2">Max OpFor: {stats['max_op']}</td>
						</tr>
						<tr>
							<td colspan="2">Max Blufor Ships: {stats['max_blu_ships']}</td>
						</tr>
                        <tr>
                            <td colspan="2">Max Opfor Ships: {stats['max_op_ships']}</td>
                        </tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
