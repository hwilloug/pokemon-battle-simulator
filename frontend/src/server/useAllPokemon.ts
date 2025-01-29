import { useQuery } from '@tanstack/react-query'

export interface Pokemon {
    name: string
    url: string
}

export interface PokemonDetail {
    name: string
    url: string
}

export const useAllPokemon = () => {
    return useQuery({
        queryKey: ['pokemon'],
        queryFn: () => fetch('https://pokeapi.co/api/v2/pokemon?limit=2000').then(res => res.json())
    })
}

export const useQueryApi = (url: string) => {
    return useQuery({
        queryKey: [url],
        queryFn: () => fetch(url).then(res => res.json()),
        enabled: !!url
    })
}